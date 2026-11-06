/**
 * Proves the evidence runner on a small real folder in Chromium: the shot names, the themes, the scroll pass, the 404 page,
 * the six verbs, the narrowing, the clients, and the stop on a bad step list. Each test writes a real step list under a
 * temp scratch folder and runs the round.
 */
import { BOOT_SCRIPT, DARK_CLASS } from "@cpc/design/lib/theme";
import { expect, test } from "@playwright/test";
import { mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { runRound } from "./evidence";
import { serveDir } from "./serve";

// The runner turns motion on, so the scroll pass, not reduced motion, is what shows a section that reveals on scroll.
test.use({ reducedMotion: "no-preference" });

/* A page in the shape of the site: dark by default, the shipped boot script, and a light and a dark color set. */
function sitePage(body: string): string {
  return `<html class="${DARK_CLASS}"><head><script>${BOOT_SCRIPT}</script><style>
    body { margin: 0; background: #ffffff; color: #111111; }
    html.${DARK_CLASS} body { background: #000000; color: #eeeeee; }
  </style></head><body>${body}</body></html>`;
}

/* A section far below the fold that fades in when it enters the viewport, as the Reveal of the site does. */
const REVEAL_PAGE = sitePage(`<main style="height:3000px">Home</main>
  <section id="late" style="height:400px;background:#ff0000;opacity:0;transition:opacity 0.2s">Late section</section>
  <script>
    new IntersectionObserver((entries, observer) => {
      for (const entry of entries) if (entry.isIntersecting) { entry.target.style.opacity = "1"; observer.disconnect(); }
    }).observe(document.getElementById("late"));
  </script>`);

type Fixture = { site: string; scratch: string; folder: (id: string) => string; lines: string[] };

/*
 * A page for the verbs. Each event that a verb sets off adds one mark to the URL hash, so the url file of a step list
 * shows which events happened: "name-<value>" for a fill, "far" and "bottom" for a scroll, "ready" for a late element.
 */
const VERBS_PAGE = sitePage(`<a id="to-week" href="/week-07/" style="display:block;height:200px;background:#0000ff">Week 7</a>
  <input id="name">
  <div id="far" style="margin-top:3000px;height:100px">Far</div>
  <div id="bottom" style="margin-top:3000px;height:100px">Bottom</div>
  <script>
    const marks = new Set();
    const mark = (word) => { marks.add(word); history.replaceState(null, "", "#" + [...marks].sort().join(".")); };
    // The link opens its page 1 s after the click, so only a step list that waits for the URL sees the new page.
    document.getElementById("to-week").addEventListener("click", (event) => {
      event.preventDefault();
      setTimeout(() => (location.href = "/week-07/"), 1000);
    });
    document.getElementById("name").addEventListener("input", (event) => mark("name-" + event.target.value));
    new IntersectionObserver((entries) => {
      for (const entry of entries) if (entry.isIntersecting) mark(entry.target.id);
    }).observe(document.getElementById("far"));
    new IntersectionObserver((entries) => {
      for (const entry of entries) if (entry.isIntersecting) mark(entry.target.id);
    }).observe(document.getElementById("bottom"));
    // Late, so a step list that does not wait sees no mark. The runner waits for networkidle, about 500 ms, first.
    // Only a route with ?late gets it, so the mark cannot change the URL while a click test waits for its page.
    if (location.search === "?late") setTimeout(() => {
      const ready = document.createElement("p");
      ready.id = "ready";
      ready.textContent = "Ready";
      document.body.prepend(ready);
      mark("ready");
    }, 3000);
  </script>`);

/* The page that the link of the verbs page opens. It is green, so a shot after the click differs from the shot before. */
const WEEK_PAGE = sitePage(`<div style="height:200px;background:#00ff00">Week 7</div>`);

/* A temp site with a home page and a 404.html, and a temp scratch root with one step list for each entry of lists. */
function fixture(lists: Record<string, unknown>): Fixture {
  const root = mkdtempSync(join(tmpdir(), "evidence-"));
  const site = join(root, "site");
  const scratch = join(root, "scratch");
  mkdirSync(site);
  writeFileSync(join(site, "index.html"), REVEAL_PAGE);
  writeFileSync(join(site, "404.html"), sitePage(`<div style="height:200px;background:#00ff00">Lost page</div>`));
  for (const [path, html] of Object.entries({ verbs: VERBS_PAGE, "week-07": WEEK_PAGE })) {
    mkdirSync(join(site, path));
    writeFileSync(join(site, path, "index.html"), html);
  }
  const folder = (id: string) => join(scratch, "demo", "evidence", id);
  for (const [id, list] of Object.entries(lists)) {
    mkdirSync(folder(id), { recursive: true });
    writeFileSync(join(folder(id), "steps.json"), JSON.stringify(list));
  }
  return { site: root, scratch, folder, lines: [] };
}

async function run(browser: import("@playwright/test").Browser, fx: Fixture): Promise<void> {
  await runRound({
    scratch: fx.scratch,
    slug: "demo",
    browser,
    serve: () => serveDir(join(fx.site, "site")),
    log: (line) => fx.lines.push(line),
  });
}

test("a route-only step list gives six shots named <width>-<theme>.png beside its steps.json", async ({ browser }) => {
  const fx = fixture({ "AT-1": { route: "/" } });
  try {
    await run(browser, fx);
    expect(readdirSync(fx.folder("AT-1")).sort()).toEqual([
      "1280-dark.png",
      "1280-light.png",
      "375-dark.png",
      "375-light.png",
      "768-dark.png",
      "768-light.png",
      "steps.json",
    ]);
  } finally {
    rmSync(fx.site, { recursive: true });
  }
});

/* The color of one pixel of a PNG as [r, g, b]. The browser decodes the file, so the test needs no image package. */
async function pixel(page: import("@playwright/test").Page, file: string, x: number, y: number): Promise<number[]> {
  const data = readFileSync(file).toString("base64");
  return page.evaluate(
    async ({ data, x, y }) => {
      const image = new Image();
      image.src = `data:image/png;base64,${data}`;
      await image.decode();
      const canvas = document.createElement("canvas");
      canvas.width = image.width;
      canvas.height = image.height;
      const context = canvas.getContext("2d")!;
      context.drawImage(image, 0, 0);
      return [...context.getImageData(x, y, 1, 1).data.slice(0, 3)];
    },
    { data, x, y },
  );
}

test("the light shot is light and the dark shot is dark", async ({ browser, page }) => {
  const fx = fixture({ "AT-1": { route: "/" } });
  try {
    await run(browser, fx);
    expect(await pixel(page, join(fx.folder("AT-1"), "1280-light.png"), 600, 10)).toEqual([255, 255, 255]);
    expect(await pixel(page, join(fx.folder("AT-1"), "1280-dark.png"), 600, 10)).toEqual([0, 0, 0]);
  } finally {
    rmSync(fx.site, { recursive: true });
  }
});

test("a section that reveals on scroll shows in the full-page shot", async ({ browser, page }) => {
  const fx = fixture({ "AT-1": { route: "/" } });
  try {
    await run(browser, fx);
    // The late section sits at 3000px to 3400px. Shown, it is red; hidden, the page background shows through.
    expect(await pixel(page, join(fx.folder("AT-1"), "375-dark.png"), 100, 3200)).toEqual([255, 0, 0]);
  } finally {
    rmSync(fx.site, { recursive: true });
  }
});

test("a missing path shows the 404.html of the folder in each shot", async ({ browser, page }) => {
  const fx = fixture({ "AT-1": { route: "/no/such/page/" } });
  try {
    await run(browser, fx);
    const shots = readdirSync(fx.folder("AT-1")).filter((file) => file.endsWith(".png"));
    expect(shots).toHaveLength(6);
    // Only the 404.html of the folder has the green band. A plain server 404 page has no color at all.
    for (const name of shots) expect(await pixel(page, join(fx.folder("AT-1"), name), 300, 100), name).toEqual([0, 255, 0]);
  } finally {
    rmSync(fx.site, { recursive: true });
  }
});

test("a bad verb, a bad key, and a bad value each stop the run before the first shot, with the file and the step named", async ({ browser }) => {
  // AT-1 is good and sorts first, so a run that checked each list only as it came to it would shoot AT-1 before it stopped.
  const cases = [
    { list: { route: "/", steps: [{ tap: "text=Week 7" }] }, error: /AT-2[/\\]steps\.json: step 1 \{"tap":"text=Week 7"\}: unknown verb "tap"/ },
    { list: { route: "/", theme: "dark" }, error: /AT-2[/\\]steps\.json: unknown key "theme"/ },
    {
      list: { route: "/", steps: [{ fill: "#name" }] },
      error: /AT-2[/\\]steps\.json: step 1 \{"fill":"#name"\}: "fill" takes \{"selector"/,
    },
    {
      list: { route: "/", steps: [{ shot: "before" }, { wait: "url" }] },
      error: /AT-2[/\\]steps\.json: step 2 \{"wait":"url"\}: "wait" "url" needs a click before it/,
    },
    { list: { route: "/", themes: ["blue"] }, error: /AT-2[/\\]steps\.json: "themes" must be a list of light, dark/ },
    { list: { route: "/", widths: [] }, error: /AT-2[/\\]steps\.json: "widths" must be a list of widths in px/ },
  ];
  for (const { list, error } of cases) {
    const fx = fixture({ "AT-1": { route: "/" }, "AT-2": list });
    try {
      await expect(run(browser, fx)).rejects.toThrow(error);
      const files = [...readdirSync(fx.folder("AT-1")), ...readdirSync(fx.folder("AT-2"))];
      expect(files.filter((file) => file.endsWith(".png"))).toEqual([]);
    } finally {
      rmSync(fx.site, { recursive: true });
    }
  }
});

/* The text of the url file of one shot, without the origin of the temp server. */
function urlOf(folder: string, name: string): string {
  const url = new URL(readFileSync(join(folder, name), "utf8"));
  return url.pathname + url.hash;
}

test("each verb runs: a click, a fill, a scroll to a selector and to the end, and a wait on a selector, the URL, and a time", async ({
  browser,
  page,
}) => {
  // Eight step lists and 14 shots, each with the scroll pass and its 1200 ms settle, take more than the default 30 s.
  test.setTimeout(120_000);
  // One width and one theme each, so the test stays fast. The narrowing has its own test.
  const one = { widths: [1280], themes: ["dark"] };
  const fx = fixture({
    "AT-1": {
      route: "/verbs/",
      steps: [{ shot: "before" }, { click: "#to-week" }, { wait: "url" }, { shot: "after-tap" }, { url: true }],
      widths: [375, 1280],
      themes: ["light", "dark"],
    },
    "AT-2": { route: "/verbs/", steps: [{ fill: { selector: "#name", value: "Ja" } }, { url: true }], ...one },
    "AT-3": { route: "/verbs/", steps: [{ scroll: "#far" }, { url: true }], ...one },
    "AT-4": { route: "/verbs/", steps: [{ scroll: "end" }, { url: true }], ...one },
    "AT-5": { route: "/verbs/?late", steps: [{ wait: "#ready" }, { url: true }], ...one },
    "AT-6": { route: "/verbs/?late", steps: [{ wait: 3500 }, { url: true }], ...one },
    // The controls: with no wait, the late element has not come yet, and the click has not opened its page yet.
    "AT-7": { route: "/verbs/?late", steps: [{ url: true }], ...one },
    // The last wait lets the page open before the shot after the last step.
    "AT-8": { route: "/verbs/", steps: [{ click: "#to-week" }, { url: true }, { wait: "url" }], ...one },
  });
  try {
    await run(browser, fx);
    // AT-1 has shot steps, so the runner takes only the named shots, and no shot after the last step.
    const names = ["before", "after-tap"].flatMap((name) =>
      [375, 1280].flatMap((width) => ["light", "dark"].map((theme) => `${name}-${width}-${theme}.png`)),
    );
    const urls = [375, 1280].flatMap((width) => ["light", "dark"].map((theme) => `url-${width}-${theme}.txt`));
    expect(readdirSync(fx.folder("AT-1")).sort()).toEqual([...names, ...urls, "steps.json"].sort());
    for (const name of urls) expect(urlOf(fx.folder("AT-1"), name), name).toBe("/week-07/");
    // The shot before the click shows the blue link; the shot after it shows the green week page.
    expect(await pixel(page, join(fx.folder("AT-1"), "before-1280-dark.png"), 300, 100)).toEqual([0, 0, 255]);
    expect(await pixel(page, join(fx.folder("AT-1"), "after-tap-1280-dark.png"), 300, 100)).toEqual([0, 255, 0]);

    // A step list with no shot step gets one shot after the last step, with the plain name.
    expect(readdirSync(fx.folder("AT-2")).sort()).toEqual(["1280-dark.png", "steps.json", "url-1280-dark.txt"]);
    expect(urlOf(fx.folder("AT-2"), "url-1280-dark.txt")).toContain("name-Ja");
    expect(urlOf(fx.folder("AT-3"), "url-1280-dark.txt")).toContain("far");
    expect(urlOf(fx.folder("AT-3"), "url-1280-dark.txt")).not.toContain("bottom");
    expect(urlOf(fx.folder("AT-4"), "url-1280-dark.txt")).toContain("bottom");
    expect(urlOf(fx.folder("AT-5"), "url-1280-dark.txt")).toContain("ready");
    expect(urlOf(fx.folder("AT-6"), "url-1280-dark.txt")).toContain("ready");
    expect(urlOf(fx.folder("AT-7"), "url-1280-dark.txt")).not.toContain("ready");
    expect(urlOf(fx.folder("AT-8"), "url-1280-dark.txt")).toMatch(/^\/verbs\//);
  } finally {
    rmSync(fx.site, { recursive: true });
  }
});

test("widths [768, 1280] writes no 375 file, and themes [light] writes no dark file", async ({ browser }) => {
  const fx = fixture({
    "AT-1": { route: "/", widths: [768, 1280] },
    "AT-2": { route: "/", themes: ["light"] },
  });
  try {
    await run(browser, fx);
    expect(readdirSync(fx.folder("AT-1")).sort()).toEqual([
      "1280-dark.png",
      "1280-light.png",
      "768-dark.png",
      "768-light.png",
      "steps.json",
    ]);
    expect(readdirSync(fx.folder("AT-2")).sort()).toEqual(["1280-light.png", "375-light.png", "768-light.png", "steps.json"]);
  } finally {
    rmSync(fx.site, { recursive: true });
  }
});

/* A serve that gives each client its own folder with its own band color, and counts each serve of each client. */
function clientServe(fx: Fixture, colors: Record<string, string>): { serve: (client: string) => ReturnType<typeof serveDir>; served: string[] } {
  const served: string[] = [];
  for (const [client, color] of Object.entries(colors)) {
    const site = join(fx.site, client);
    mkdirSync(site);
    writeFileSync(join(site, "index.html"), sitePage(`<div style="height:200px;background:${color}">${client}</div>`));
  }
  return {
    served,
    serve: (client) => {
      served.push(client);
      return serveDir(join(fx.site, client));
    },
  };
}

test("two tests with two clients serve each client one time and put the client first in each file name", async ({ browser, page }) => {
  // Two tests in two clients take 24 shots, each with its scroll pass, so the run needs more than the default 30 s.
  test.setTimeout(120_000);
  const both = { route: "/", clients: ["cpc", "norcal"] };
  const fx = fixture({ "AT-1": both, "AT-2": both });
  const site = clientServe(fx, { cpc: "#0000ff", norcal: "#ffff00" });
  try {
    await runRound({ scratch: fx.scratch, slug: "demo", browser, serve: site.serve, log: (line) => fx.lines.push(line) });
    expect(site.served).toEqual(["cpc", "norcal"]);
    for (const id of ["AT-1", "AT-2"]) {
      const shots = readdirSync(fx.folder(id)).filter((file) => file.endsWith(".png"));
      expect(shots.sort()).toEqual(
        ["cpc", "norcal"].flatMap((client) => [375, 768, 1280].flatMap((width) => [`${client}-${width}-dark.png`, `${client}-${width}-light.png`])).sort(),
      );
      expect(await pixel(page, join(fx.folder(id), "cpc-1280-dark.png"), 300, 100)).toEqual([0, 0, 255]);
      expect(await pixel(page, join(fx.folder(id), "norcal-1280-dark.png"), 300, 100)).toEqual([255, 255, 0]);
    }
  } finally {
    rmSync(fx.site, { recursive: true });
  }
});

test("a test with no clients key shoots cpc with no prefix, and a test of one client gets no prefix", async ({ browser, page }) => {
  const fx = fixture({ "AT-1": { route: "/" }, "AT-2": { route: "/", clients: ["norcal"] } });
  const site = clientServe(fx, { cpc: "#0000ff", norcal: "#ffff00" });
  const plain = [375, 768, 1280].flatMap((width) => [`${width}-dark.png`, `${width}-light.png`]).sort();
  try {
    await runRound({ scratch: fx.scratch, slug: "demo", browser, serve: site.serve, log: (line) => fx.lines.push(line) });
    expect(site.served).toEqual(["cpc", "norcal"]);
    expect(readdirSync(fx.folder("AT-1")).filter((file) => file.endsWith(".png")).sort()).toEqual(plain);
    expect(readdirSync(fx.folder("AT-2")).filter((file) => file.endsWith(".png")).sort()).toEqual(plain);
    expect(await pixel(page, join(fx.folder("AT-1"), "1280-dark.png"), 300, 100)).toEqual([0, 0, 255]);
    expect(await pixel(page, join(fx.folder("AT-2"), "1280-dark.png"), 300, 100)).toEqual([255, 255, 0]);
  } finally {
    rmSync(fx.site, { recursive: true });
  }
});

test("a bad clients value stops the run before the first shot, with the file named", async ({ browser }) => {
  for (const clients of ["cpc", [], ["cpc", "cpc"], [7]]) {
    const fx = fixture({ "AT-1": { route: "/" }, "AT-2": { route: "/", clients } });
    try {
      await expect(run(browser, fx)).rejects.toThrow(/AT-2[/\\]steps\.json: "clients" must be a list of distinct client slugs/);
      expect(readdirSync(fx.folder("AT-1")).filter((file) => file.endsWith(".png"))).toEqual([]);
    } finally {
      rmSync(fx.site, { recursive: true });
    }
  }
});

test("a test with two clients puts the client first in a named shot and in the url file", async ({ browser }) => {
  const fx = fixture({
    "AT-1": { route: "/", steps: [{ shot: "top" }, { url: true }], widths: [1280], themes: ["dark"], clients: ["cpc", "norcal"] },
  });
  const site = clientServe(fx, { cpc: "#0000ff", norcal: "#ffff00" });
  try {
    await runRound({ scratch: fx.scratch, slug: "demo", browser, serve: site.serve, log: (line) => fx.lines.push(line) });
    expect(readdirSync(fx.folder("AT-1")).sort()).toEqual([
      "cpc-top-1280-dark.png",
      "cpc-url-1280-dark.txt",
      "norcal-top-1280-dark.png",
      "norcal-url-1280-dark.txt",
      "steps.json",
    ]);
  } finally {
    rmSync(fx.site, { recursive: true });
  }
});
