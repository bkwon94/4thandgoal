/**
 * Proves the smoke run on small real pages: the two sizes in the light theme, and each cause that fails a flow.
 * Each test serves a temp site, runs real flows in WebKit and Chromium, and reads the log and the shots.
 */
import { expect, test } from "@playwright/test";
import { mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { serveDir } from "./serve";
import { addSteps, type Flow, latestWeek, readFlows, runSmoke } from "./smoke";

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
});

test("a green flow passes with one light shot at 390 in WebKit and one at 1280, and the log says so", async () => {
  const { result, lines, out } = await smoke({ week: WEEK_PAGE }, [week([{ expect: "text=Week 10" }])]);
  expect(result.failures).toEqual([]);
  expect(readdirSync(join(out, "week-report")).sort()).toEqual(["1280-light.png", "390-light.png"]);
  expect(lines).toContainEqual(expect.stringMatching(/^PASS Week report 390x660 webkit/));
  expect(lines).toContainEqual(expect.stringMatching(/^PASS Week report 1280x800 chromium/));
  expect(lines.at(-1)).toBe("Smoke run: 1 flow, 1 passed, 0 failed");
  expect(readFileSync(join(out, "smoke.log"), "utf8")).toBe(`${lines.join("\n")}\n`);
});

test("a failed expect of Week 99 fails the run, names the flow and the step, and keeps a shot of the failure", async () => {
  const { result, lines, out } = await smoke({ week: WEEK_PAGE }, [week([{ expect: "text=Week 10" }, { expect: "text=Week 99" }])]);
  const cause = 'step 2 {"expect":"text=Week 99"}: the expect failed: "text=Week 99" is not visible';
  expect(result.failures).toEqual([`FAIL Week report 390x660 webkit: ${cause} after 5000 ms`, `FAIL Week report 1280x800 chromium: ${cause} after 5000 ms`]);
  expect(lines.at(-1)).toBe("Smoke run: 1 flow, 0 passed, 1 failed");
  expect(readdirSync(join(out, "week-report")).sort()).toEqual(["fail-1280-light.png", "fail-390-light.png"]);
});

test("a click on a missing element fails the run and names the step", async () => {
  const { result } = await smoke({ week: WEEK_PAGE }, [week([{ click: "text=Grade the Trade" }])]);
  expect(result.failures).toHaveLength(2);
  for (const line of result.failures) expect(line).toMatch(/^FAIL Week report \S+ \w+: step 1 \{"click":"text=Grade the Trade"\}: .*Timeout 10000ms/);
});

/* The week page with a seeded style that moves the nav up over the title. */
const OVERLAP_PAGE = WEEK_PAGE.replace('<nav aria-label="Chapters">', '<nav aria-label="Chapters" style="position:absolute;top:20px;left:16px">');

test("a seeded overlap fails the run and names the two elements", async () => {
  const { result } = await smoke({ week: OVERLAP_PAGE }, [week([{ expect: "text=Week 10" }])]);
  expect(result.failures).toHaveLength(2);
  for (const line of result.failures) expect(line).toMatch(/: overlap: <h1> "Week 10" and <a> "Matchup of the Week"$/);
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
    expect(failures).toContainEqual(`FAIL Called 1280x800 chromium: API error: 404 POST ${api}/grade`);
  } finally {
    await server.close();
  }
});

test("the latest week is the highest week of the highest season of the published folder", () => {
  const { dir } = site({ "2025/week-17": "", "2026/week-09": "", "2026/week-10": "", "2026/week-06": "" });
  writeFileSync(join(dir, "2026", "managers.json"), "{}");
  expect(latestWeek(dir)).toBe("/2026/week-10/");
});

test("the flow list of the verify skill reads clean, and the Week report opens the latest week", () => {
  const flows = readFlows(join(process.cwd(), "..", "..", ".claude", "skills", "verify", "flows.json"));
  const report = flows.find((flow) => flow.name === "Week report");
  expect(report?.route).toBe("{latest-week}");
  expect(report?.steps.some((step) => "expect" in step)).toBe(true);
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
