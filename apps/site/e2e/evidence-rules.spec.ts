/**
 * Proves the evidence runner on a small real folder in Chromium: the shot names, the themes, the scroll pass, the 404 page,
 * and the stop on a bad step list. Each test writes a real step list under a temp scratch folder and runs the round.
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

/* A temp site with a home page and a 404.html, and a temp scratch root with one step list for each entry of lists. */
function fixture(lists: Record<string, unknown>): Fixture {
  const root = mkdtempSync(join(tmpdir(), "evidence-"));
  const site = join(root, "site");
  const scratch = join(root, "scratch");
  mkdirSync(site);
  writeFileSync(join(site, "index.html"), REVEAL_PAGE);
  writeFileSync(join(site, "404.html"), sitePage(`<div style="height:200px;background:#00ff00">Lost page</div>`));
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

test("a bad verb and a bad key each stop the run before the first shot, with the file and the step named", async ({ browser }) => {
  // AT-1 is good and sorts first, so a run that checked each list only as it came to it would shoot AT-1 before it stopped.
  const cases = [
    { list: { route: "/", steps: [{ tap: "text=Week 7" }] }, error: /AT-2[/\\]steps\.json: step 1 \{"tap":"text=Week 7"\}: unknown verb "tap"/ },
    { list: { route: "/", theme: "dark" }, error: /AT-2[/\\]steps\.json: unknown key "theme"/ },
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
