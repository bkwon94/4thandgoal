/**
 * Proves the smoke run on small real pages: the two sizes in the light theme, and each cause that fails a flow.
 * Each test serves a temp site, runs real flows in WebKit and Chromium, and reads the log and the shots.
 */
import { expect, test } from "@playwright/test";
import { mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import type { AddressInfo } from "node:net";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { serveDir } from "./serve";
import {
  addSteps,
  type Flow,
  flowsOfBuild,
  latestWeek,
  readFlows,
  routeOf,
  runSmoke,
  tradesClosedOf,
} from "./smoke";

// Each smoke run starts two browsers and shoots each flow at two sizes, so a test takes more than the default 30 s.
test.describe.configure({ timeout: 120_000 });

/* A plain light page with a title. */
const WEEK_PAGE = `<html><body style="margin:0;background:#fff;color:#111">
  <h1 style="margin:16px;font-size:32px">Week 10</h1>
  <nav aria-label="Chapters"><a href="#motw">Matchup of the Week</a></nav>
</body></html>`;

/* The temp roots of the running test. The hook below removes them. */
const roots: string[] = [];

test.afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true });
});

/* A temp site with one page per entry of pages, and a temp out folder for the smoke run. */
function site(pages: Record<string, string>): { dir: string; out: string } {
  const root = mkdtempSync(join(tmpdir(), "smoke-"));
  roots.push(root);
  const dir = join(root, "site");
  for (const [path, html] of Object.entries(pages)) {
    mkdirSync(join(dir, path), { recursive: true });
    writeFileSync(join(dir, path, "index.html"), html);
  }
  return { dir, out: join(root, "out") };
}

/* Runs the flows on the temp site, and gives the result and the lines of the log. */
async function smoke(pages: Record<string, string>, flows: Flow[]) {
  const { dir, out } = site(pages);
  const server = await serveDir(dir);
  const lines: string[] = [];
  try {
    const result = await runSmoke({ flows, url: server.url, out, log: (line) => lines.push(line) });
    return { result, lines, out };
  } finally {
    await server.close();
  }
}

const week = (steps: Flow["steps"]): Flow => ({
  name: "Week report",
  globs: ["apps/site/src/app/_routes/week/**"],
  route: "/week/",
  steps,
  expected: 'The title "Week N" and the chapter rail',
  claude: false,
  layout: false,
});

test("a green flow passes with one light shot at 390 in WebKit and one at 1280, and the log says so", async () => {
  const { result, lines, out } = await smoke({ week: WEEK_PAGE }, [
    week([{ expect: "text=Week 10" }]),
  ]);
  expect(result.failures).toEqual([]);
  expect(readdirSync(join(out, "week-report")).sort()).toEqual(["1280-light.png", "390-light.png"]);
  expect(lines).toContainEqual(expect.stringMatching(/^PASS Week report 390x660 webkit/));
  expect(lines).toContainEqual(expect.stringMatching(/^PASS Week report 1280x800 chromium/));
  expect(lines.at(-1)).toBe("Smoke run: 1 flow, 1 passed, 0 failed");
  expect(readFileSync(join(out, "smoke.log"), "utf8")).toBe(`${lines.join("\n")}\n`);
});

test("a layout flow adds the two iPad sizes, and a flow with no layout flag keeps the two smoke sizes", async () => {
  const flows = [
    { ...week([{ expect: "text=Week 10" }]), layout: true },
    { ...week([{ expect: "text=Week 10" }]), name: "Passphrase" },
  ];
  const { result, lines, out } = await smoke({ week: WEEK_PAGE }, flows);
  expect(result.failures).toEqual([]);
  expect(readdirSync(join(out, "week-report")).sort()).toEqual([
    "1080-light.png",
    "1280-light.png",
    "390-light.png",
    "810-light.png",
  ]);
  expect(readdirSync(join(out, "passphrase")).sort()).toEqual(["1280-light.png", "390-light.png"]);
  expect(lines).toContainEqual(expect.stringMatching(/^PASS Week report 810x980 webkit/));
  expect(lines).toContainEqual(expect.stringMatching(/^PASS Week report 1080x740 webkit/));
});

test("a flow that calls Claude runs once, at 390 in WebKit, even when it is a layout flow", async () => {
  const { result, lines, out } = await smoke({ week: WEEK_PAGE }, [
    { ...week([{ expect: "text=Week 10" }]), claude: true, layout: true },
  ]);
  expect(result.failures).toEqual([]);
  expect(readdirSync(join(out, "week-report"))).toEqual(["390-light.png"]);
  expect(lines.filter((line) => line.startsWith("PASS"))).toEqual([
    expect.stringMatching(/^PASS Week report 390x660 webkit/),
  ]);
});

test("a flow with no Claude flag or no layout flag stops the run, and the error names the flow", () => {
  const { dir } = site({});
  mkdirSync(dir, { recursive: true });
  const file = join(dir, "flows.json");
  const { claude: _claude, ...flow } = week([]);
  writeFileSync(file, JSON.stringify([flow]));
  expect(() => readFlows(file)).toThrow(/flow 1 "Week report": "claude" must be true or false/);
  writeFileSync(file, JSON.stringify([{ ...week([]), layout: "yes" }]));
  expect(() => readFlows(file)).toThrow(/flow 1 "Week report": "layout" must be true or false/);
});

test("a failed expect of Week 99 fails the run, names the flow and the step, and keeps a shot of the failure", async () => {
  const { result, lines, out } = await smoke({ week: WEEK_PAGE }, [
    week([{ expect: "text=Week 10" }, { expect: "text=Week 99" }]),
  ]);
  const cause =
    'step 2 {"expect":"text=Week 99"}: the expect failed: "text=Week 99" is not visible';
  expect(result.failures).toEqual([
    `FAIL Week report 390x660 webkit: ${cause} after 5000 ms`,
    `FAIL Week report 1280x800 chromium: ${cause} after 5000 ms`,
  ]);
  expect(lines.at(-1)).toBe("Smoke run: 1 flow, 0 passed, 1 failed");
  expect(readdirSync(join(out, "week-report")).sort()).toEqual([
    "fail-1280-light.png",
    "fail-390-light.png",
  ]);
});

test("a click on a missing element fails the run and names the step", async () => {
  const { result } = await smoke({ week: WEEK_PAGE }, [week([{ click: "text=Grade the Trade" }])]);
  expect(result.failures).toHaveLength(2);
  for (const line of result.failures)
    expect(line).toMatch(
      /^FAIL Week report \S+ \w+: step 1 \{"click":"text=Grade the Trade"\}: .*Timeout 10000ms/,
    );
});

/* The week page with a seeded style that moves the nav up over the title. */
const OVERLAP_PAGE = WEEK_PAGE.replace(
  '<nav aria-label="Chapters">',
  '<nav aria-label="Chapters" style="position:absolute;top:20px;left:16px">',
);

test("a seeded overlap fails the run and names the two elements", async () => {
  const { result } = await smoke({ week: OVERLAP_PAGE }, [week([{ expect: "text=Week 10" }])]);
  expect(result.failures).toHaveLength(2);
  for (const line of result.failures)
    expect(line).toMatch(/: overlap: <h1> "Week 10" and <a> "Matchup of the Week"$/);
});

/* The week page with a screen-reader text on top of the title, as the class sr-only of Tailwind sets it. */
const SR_ONLY_PAGE = WEEK_PAGE.replace(
  "</h1>",
  '<span style="position:absolute;top:16px;left:16px;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap">Up 6</span></h1>',
);

test("a screen-reader text over a visible text is no overlap, because its own box clips it", async () => {
  const { result } = await smoke({ week: SR_ONLY_PAGE }, [week([{ expect: "text=Week 10" }])]);
  expect(result.failures).toEqual([]);
});

/* The week page with a modal layer over the title, as a Stop card of the Tour sits over the dim page. */
const MODAL_PAGE = (layer: string) =>
  WEEK_PAGE.replace(
    "</body>",
    `<div role="dialog" aria-modal="true" style="position:fixed;top:8px;left:8px;width:300px;background:#fff">${layer}</div></body>`,
  );

test("a modal layer over a text of the page is no overlap, but two texts inside the layer still overlap", async () => {
  const clear = await smoke(
    { week: MODAL_PAGE('<p style="margin:16px;font-size:20px">Suggestions</p>') },
    [week([{ expect: "text=Week 10" }])],
  );
  expect(clear.result.failures).toEqual([]);
  const seeded = MODAL_PAGE(
    '<p style="margin:16px">Suggestions</p><p style="position:absolute;top:16px;left:16px;margin:0">Checked</p>',
  );
  const { result } = await smoke({ week: seeded }, [week([{ expect: "text=Week 10" }])]);
  expect(result.failures).toHaveLength(2);
  for (const line of result.failures)
    expect(line).toMatch(
      /: overlap: <p> "Suggestions" and <p> "Checked"$|: overlap: <p> "Checked" and <p> "Suggestions"$/,
    );
});

/* The week page with a paragraph of tight leading: each glyph box is taller than its line, so two lines share a few px. */
const TIGHT_PAGE = WEEK_PAGE.replace(
  "</body>",
  `<p style="width:280px;margin:16px;font-size:16px;line-height:0.9"><span style="font-weight:700">Maye d'force B with U</span> leads by 165.8 points over the line.</p></body>`,
);

test("two lines of one paragraph with tight leading are no overlap, because each line owns only its line height", async () => {
  const { result } = await smoke({ week: TIGHT_PAGE }, [week([{ expect: "text=Week 10" }])]);
  expect(result.failures).toEqual([]);
});

test("a page error, a console error, and an API response of 4xx each fail the run", async () => {
  const pages = {
    thrown: `<html><body><h1>Week 10</h1><script>throw new Error("boom")</script></body></html>`,
    logged: `<html><body><h1>Week 10</h1><script>console.error("bad data")</script></body></html>`,
    // The site server stands in the place of the API, so the call needs no CORS. It has no /api/grade, so it gets a 404.
    called: `<html><body><h1>Week 10</h1><script>fetch("/api/grade", { method: "POST" })</script></body></html>`,
  };
  const flows: Flow[] = [
    { ...week([]), name: "Thrown", route: "/thrown/" },
    { ...week([]), name: "Logged", route: "/logged/" },
    { ...week([]), name: "Called", route: "/called/" },
  ];
  const { dir, out } = site(pages);
  const server = await serveDir(dir);
  try {
    const api = `${server.url}/api`;
    const { failures } = await runSmoke({ flows, url: server.url, api, out, log: () => {} });
    expect(failures).toContainEqual("FAIL Thrown 390x660 webkit: page error: boom");
    expect(failures).toContainEqual("FAIL Thrown 1280x800 chromium: page error: boom");
    expect(failures).toContainEqual("FAIL Logged 390x660 webkit: console error: bad data");
    expect(failures).toContainEqual("FAIL Logged 1280x800 chromium: console error: bad data");
    expect(failures).toContainEqual(`FAIL Called 390x660 webkit: API error: 404 POST ${api}/grade`);
    expect(failures).toContainEqual(
      `FAIL Called 1280x800 chromium: API error: 404 POST ${api}/grade`,
    );
  } finally {
    await server.close();
  }
});

/* A stand-in API on a free port. It answers each path with a 200 and allows each origin, so only the guard can fail a call. */
async function standInApi(): Promise<{ url: string; close: () => Promise<void> }> {
  const server = createServer((request, response) => {
    response.setHeader("access-control-allow-origin", "*");
    response.end("ok");
  });
  await new Promise<void>((done) => server.listen(0, "127.0.0.1", done));
  const { port } = server.address() as AddressInfo;
  return {
    url: `http://127.0.0.1:${port}`,
    close: () => new Promise<void>((done) => server.close(() => done())),
  };
}

test("two runs at the same time each call only their own API, and a call to the API of the other run fails the run", async () => {
  const [apiA, apiB] = [await standInApi(), await standInApi()];
  const call = (api: string) =>
    `<html><body><h1>Week 10</h1><script>fetch("${api}/health")</script></body></html>`;
  // The page of run A calls the API of run B. The page of run B calls its own API.
  const a = site({ week: call(apiB.url) });
  const b = site({ week: call(apiB.url) });
  const [siteA, siteB] = [await serveDir(a.dir), await serveDir(b.dir)];
  try {
    const flows = [week([{ expect: "text=Week 10" }])];
    const [runA, runB] = await Promise.all([
      runSmoke({ flows, url: siteA.url, api: apiA.url, out: a.out, log: () => {} }),
      runSmoke({ flows, url: siteB.url, api: apiB.url, out: b.out, log: () => {} }),
    ]);
    expect(runA.failures).toEqual([
      `FAIL Week report 390x660 webkit: foreign local call: GET ${apiB.url}/health`,
      `FAIL Week report 1280x800 chromium: foreign local call: GET ${apiB.url}/health`,
    ]);
    expect(runB.failures).toEqual([]);
  } finally {
    for (const server of [siteA, siteB, apiA, apiB]) await server.close();
  }
});

test("a failed image of another host is no error, because the page swaps it, but a missing file of the site fails the run", async () => {
  // The host stands in for an image host such as the CDN of Sleeper. The name .invalid never resolves, so each image fails.
  // A local server cannot stand in, because a call to a local server that is not of the run fails the run.
  const host = { url: "http://cdn.invalid" };
  const image = (src: string) =>
    `<html><body><h1>Week 10</h1><img src="${src}" alt="" onerror="this.dataset.fallback = 1"></body></html>`;
  const flows: Flow[] = [
    { ...week([]), name: "Other host", route: "/other/" },
    { ...week([]), name: "Own site", route: "/own/" },
  ];
  const { dir, out } = site({
    other: image(`${host.url}/players/SF.jpg`),
    own: image("/players/SF.jpg"),
  });
  const server = await serveDir(dir);
  try {
    const { failures } = await runSmoke({ flows, url: server.url, out, log: () => {} });
    expect(failures.filter((line) => line.includes("Other host"))).toEqual([]);
    expect(failures.filter((line) => line.includes("Own site"))).toEqual([
      expect.stringMatching(
        /^FAIL Own site 390x660 webkit: console error: Failed to load resource/,
      ),
      expect.stringMatching(
        /^FAIL Own site 1280x800 chromium: console error: Failed to load resource/,
      ),
    ]);
  } finally {
    await server.close();
  }
});

test("the latest week is the highest week of the highest season of the published folder", () => {
  const { dir } = site({
    "2025/week-17": "",
    "2026/week-09": "",
    "2026/week-10": "",
    "2026/week-06": "",
  });
  writeFileSync(join(dir, "2026", "managers.json"), "{}");
  expect(latestWeek(dir)).toBe("/2026/week-10/");
});

test("a route names the latest week as {latest-week} and the latest season as {season}", () => {
  const { dir } = site({ "2025/week-17": "", "2026/week-09": "", "2026/week-10": "" });
  expect(routeOf("{latest-week}", dir)).toBe("/2026/week-10/");
  expect(routeOf("/{season}/managers/", dir)).toBe("/2026/managers/");
  expect(routeOf("/midseason/{season}/", dir)).toBe("/midseason/2026/");
  expect(routeOf("/rankings/", dir)).toBe("/rankings/");
});

test("the flow list of the verify skill reads clean, and the Week report opens the latest week", () => {
  const flows = readFlows(
    join(process.cwd(), "..", "..", ".claude", "skills", "verify", "flows.json"),
  );
  const report = flows.find((flow) => flow.name === "Week report");
  expect(report?.route).toBe("{latest-week}");
  expect(report?.steps.some((step) => "expect" in step)).toBe(true);
});

/*
 * A first-visit reader picks a team, and then the first-visit Tour shows about 0.9 s later, before the reader taps anything.
 * A flow that taps a Topic at once beats the Tour, and the Tour then opens later, over the answer, on its dim. So each
 * flow of the front door skips the Tour right after the team pick, as a first-visit reader does.
 */
test("each flow of the front door skips the first-visit Tour right after the team pick", () => {
  const flows = readFlows(
    join(process.cwd(), "..", "..", ".claude", "skills", "verify", "flows.json"),
  );
  const pick = { click: 'role=dialog[name="Which team is yours?"] >> role=button' };
  const skip = { click: 'role=dialog[name="Suggestions"] >> role=button[name="Skip"]' };
  const door = flows.filter((flow) =>
    flow.steps.some((step) => JSON.stringify(step) === JSON.stringify(pick)),
  );
  expect(door.map((flow) => flow.name)).toEqual(["Front door", "Passphrase"]);
  for (const flow of door) {
    const at = flow.steps.findIndex((step) => JSON.stringify(step) === JSON.stringify(pick));
    expect(flow.steps[at + 1], flow.name).toEqual(skip);
  }
});

test("added steps go after the steps of their flow, and a name with no picked flow stops the run", () => {
  const { dir } = site({});
  mkdirSync(dir, { recursive: true });
  const file = join(dir, "steps.json");
  writeFileSync(file, JSON.stringify({ "Week report": [{ expect: "text=Week 99" }] }));
  const [flow] = addSteps([week([{ expect: "text=Week 10" }])], file);
  expect(flow.steps).toEqual([{ expect: "text=Week 10" }, { expect: "text=Week 99" }]);
  writeFileSync(file, JSON.stringify({ Analyzer: [{ expect: "text=Lean" }] }));
  expect(() => addSteps([week([])], file)).toThrow(/no picked flow is named "Analyzer"/);
});

test("a closed build runs the closedSteps of a flow, and an open build keeps its steps", () => {
  const flow: Flow = {
    ...week([{ expect: "text=Week 10" }]),
    closedSteps: [{ expect: "text=Closed" }],
  };
  expect(flowsOfBuild([flow], true)[0].steps).toEqual([{ expect: "text=Closed" }]);
  expect(flowsOfBuild([flow], false)[0].steps).toEqual([{ expect: "text=Week 10" }]);
  const plain = week([{ expect: "text=Week 10" }]);
  expect(flowsOfBuild([plain], true)[0].steps).toEqual(plain.steps);
});

test("the build value of Trades closed comes from the generated client values, never the clock", () => {
  const { dir } = site({});
  mkdirSync(dir, { recursive: true });
  const file = join(dir, "client-values.ts");
  writeFileSync(file, 'export const clientValues = {\n  "tradesClosed": true,\n};\n');
  expect(tradesClosedOf(file)).toBe(true);
  writeFileSync(file, 'export const clientValues = {\n  "tradesClosed": false,\n};\n');
  expect(tradesClosedOf(file)).toBe(false);
  writeFileSync(file, "export const clientValues = {};\n");
  expect(() => tradesClosedOf(file)).toThrow(/no tradesClosed value/);
});

test("the Analyzer flow has closedSteps that expect the closed line and the Home link", () => {
  const flows = readFlows(
    join(process.cwd(), "..", "..", ".claude", "skills", "verify", "flows.json"),
  );
  const closed = flows.find((flow) => flow.name === "Analyzer")?.closedSteps;
  expect(closed).toContainEqual({
    expect: "text=The trade deadline has passed. Trades open again next season.",
  });
  expect(closed).toContainEqual({ expect: 'main >> role=link[name="Home"]' });
  expect(closed?.some((step) => "shot" in step)).toBe(true);
});
