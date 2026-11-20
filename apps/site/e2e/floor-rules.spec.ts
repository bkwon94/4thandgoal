/**
 * Proves each rule of the readability floor on a small real page in Chromium, so the floor fails on what it must fail.
 * Each page is plain HTML that the browser lays out, so the scans measure real boxes, sizes, and colors.
 */
import { BOOT_SCRIPT, DARK_CLASS } from "@cpc/design/lib/theme";
import { expect, test, type Page } from "@playwright/test";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  openPage,
  scanAxe,
  scanContrast,
  scanScroll,
  scanTargets,
  scanText,
  scanWords,
} from "./floor";
import { serveDir } from "./serve";

const PHONE = { width: 390, height: 844 };

test("prose under 16px fails and names the element and the size", async ({ page }) => {
  await page.setViewportSize(PHONE);
  await page.setContent(
    `<main><p class="blurb" style="font-size:14px">A short blurb of the week.</p></main>`,
  );
  const scan = await scanText(page);
  expect(scan.failures).toEqual([expect.stringMatching(/p\.blurb .*14px.*prose.*16px/)]);
});

test("other text under 11px fails, 11px passes, and the scan counts each tier", async ({
  page,
}) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<main>
    <span class="eyebrow" style="font-size:11px">Week 8</span>
    <span class="dock" style="font-size:10px">Home</span>
    <div data-prose style="font-size:16px">A recap with a <b>bold</b> word.</div>
    <p style="font-size:16px">A blurb.</p>
  </main>`);
  const scan = await scanText(page);
  expect(scan.failures).toEqual([
    expect.stringMatching(/span\.dock "Home" is 10px.*other text.*11px/),
  ]);
  expect(scan).toMatchObject({ prose: 3, other: 2 });
});

test("a link or button under 44px fails, and a link inside prose is exempt and listed", async ({
  page,
}) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<main>
    <a class="row" href="/a" style="display:block;height:48px">A whole row</a>
    <button class="close" style="width:30px;height:30px">x</button>
    <p style="font-size:16px">Read the <a class="inline" href="/b">manager page</a> next.</p>
  </main>`);
  const scan = await scanTargets(page);
  expect(scan.failures).toEqual([
    expect.stringMatching(/button\.close "x" is 30x30px, under the tap floor of 44px/),
  ]);
  expect(scan.exempt).toEqual([expect.stringMatching(/a\.inline "manager page"/)]);
});

test("a sideways scroll at 390px fails and names the widest element, and a box that scrolls itself passes", async ({
  page,
}) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<body style="margin:0">
    <div style="overflow-x:auto"><table style="width:900px"><tr><td>A wide table in its own box</td></tr></table></div>
  </body>`);
  expect(await scanScroll(page)).toEqual([]);

  await page.setContent(
    `<body style="margin:0"><div class="strip" style="width:500px">A strip of weeks</div></body>`,
  );
  expect(await scanScroll(page)).toEqual([
    expect.stringMatching(/scrolls sideways: 500px wide in 390px.*div\.strip/),
  ]);
});

test("a word split over two lines fails and names the word, and a wrap between words or after a hyphen passes", async ({
  page,
}) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<body style="margin:0;overflow-wrap:break-word;font:12px monospace">
    <div class="tile" style="width:60px">UNDERPERFORMER</div>
    <div class="wrap" style="width:60px">TOP SCORER</div>
    <div class="hyphen" style="width:40px">my 5-game</div>
    <div class="cut" style="width:60px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">BENCHWARMER</div>
  </body>`);
  expect(await scanWords(page)).toEqual([
    expect.stringMatching(/div\.tile .*"UNDERPERFORMER" breaks over 2 lines/),
  ]);
});

test("axe color-contrast fails on a violation and on an incomplete result, and passes a clear pair", async ({
  page,
}) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<main style="background:#fff">
    <p class="clear" style="color:#111">Clear text.</p>
    <p class="faint" style="color:#bbb">Faint text.</p>
    <div style="background:linear-gradient(#000,#fff)"><p class="glow" style="color:#777">Text on a glow.</p></div>
  </main>`);
  const failures = await scanContrast(page);
  expect(failures).toHaveLength(2);
  expect(failures).toEqual(
    expect.arrayContaining([
      expect.stringMatching(/^violation: \.faint .*contrast/),
      expect.stringMatching(/^incomplete: \.glow /),
    ]),
  );
});

/*
 * A hero as HeroFrame renders it: a section on the band color, an art layer with the glow and the grid, and the content
 * over it. The glow sits at the top left here, under the start of the content, so a test can put text on its bright part.
 */
const hero = (label: string, glow: string, content: string) => `<section aria-label="${label}"
    style="position:relative;overflow:hidden;background:#101418;color:#f5f5f5;padding:24px">
    <div aria-hidden="true"><div data-hero-art="texture" style="position:absolute;inset:0;background-image:
      radial-gradient(ellipse 60% 80% at 0% 0%, ${glow}, transparent 70%),
      linear-gradient(#2a2f36 1px, transparent 1px), linear-gradient(90deg, #2a2f36 1px, transparent 1px);
      background-size:100% 100%, 24px 24px, 24px 24px"></div></div>
    <div style="position:relative">${content}</div>
  </section>`;

test("hero text over the art passes on its pixels, and an incomplete result outside a hero still fails and names it", async ({
  page,
}) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<main style="background:#fff">
    ${hero("Week 9", "#3a1418", `<h1 class="title" style="font-size:32px">Week 9</h1><p class="meta" style="font-size:16px">A clear meta line.</p>`)}
    <div style="background:linear-gradient(#000,#fff)"><p class="glow" style="color:#777">Text on a glow.</p></div>
  </main>`);
  const failures = await scanContrast(page);
  expect(failures).toEqual([expect.stringMatching(/^incomplete: \.glow /)]);
});

test("hero text that the glow makes faint fails, and the failure names the hero, the text, the ratio, and the pixel", async ({
  page,
}) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<main style="background:#fff">
    ${hero("Manager", "#ff4040", `<p class="muted" style="font-size:16px;color:#9a9a9a">A muted line on the glow.</p>`)}
  </main>`);
  const failures = await scanContrast(page);
  expect(failures).toEqual([
    expect.stringMatching(
      /^pixel: hero "Manager" p\.muted "A muted line on the glow\." is \d\.\d\d:1 on #[0-9a-f]{6}, under 4\.5:1$/,
    ),
  ]);
});

test("a short text of a hero, which axe cannot judge, is rated on its pixels, and a short text outside a hero still fails", async ({
  page,
}) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<main style="background:#fff">
    ${hero("Chips", "#ff4040", `<p style="font-size:16px;color:#f5f5f5">A clear line.</p><span class="chip" style="display:block;font-size:16px;color:#7a7a7a">7</span><span class="ok" style="display:block;font-size:16px;color:#ffffff">8</span>`)}
    <p class="short" style="color:#777">7</p>
  </main>`);
  const failures = await scanContrast(page);
  expect(failures).toEqual(
    expect.arrayContaining([
      expect.stringMatching(
        /^pixel: hero "Chips" span\.chip "7" is \d\.\d\d:1 on #[0-9a-f]{6}, under 4\.5:1$/,
      ),
    ]),
  );
  expect(failures.filter((line) => line.startsWith("pixel:"))).toHaveLength(1);
  expect(failures).toEqual(
    expect.arrayContaining([expect.stringMatching(/^incomplete: \.short .*too short/)]),
  );
});

test("an aria-hidden text of a hero is rated on its pixels", async ({ page }) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<main style="background:#fff">
    ${hero("Art text", "#ff4040", `<p style="font-size:16px;color:#f5f5f5">A clear line.</p><div aria-hidden="true" class="art" style="font-size:48px;color:#9a9a9a">404</div>`)}
  </main>`);
  const failures = await scanContrast(page);
  expect(failures).toEqual([
    expect.stringMatching(
      /^pixel: hero "Art text" div\.art "404" is \d\.\d\d:1 on #[0-9a-f]{6}, under 4\.5:1$/,
    ),
  ]);
});

test("a hero where the pixel scan finds no text fails and names the hero", async ({ page }) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<main style="background:#fff">
    ${hero("Empty stage", "#3a1418", `<div style="height:120px"></div><span style="position:absolute;width:1px;height:1px;overflow:hidden">Hidden note</span>`)}
  </main>`);
  const failures = await scanContrast(page);
  expect(failures).toEqual([
    expect.stringMatching(/^pixel: hero "Empty stage": the pixel scan finds no text$/),
  ]);
});

test("the egg banner is a hero of its own, so the pixel scan reads its line over the hero texture", async ({
  page,
}) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<main style="background:#fff">
    <section aria-label="Egg drop" class="hero-texture" style="background:#101418 radial-gradient(ellipse 60% 80% at 0% 0%, #ff4040, transparent 70%);color:#f5f5f5;padding:8px">
      <span class="line" style="font-size:16px;color:#9a9a9a">3 eggs dropped</span>
    </section>
  </main>`);
  const failures = await scanContrast(page);
  expect(failures).toEqual([
    expect.stringMatching(/^pixel: hero "Egg drop" span\.line "3 eggs dropped" is \d\.\d\d:1/),
  ]);
});

test("axe color-contrast with a scope checks only the open part, so text that the open part covers passes", async ({
  page,
}) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<main style="background:#fff">
    <p class="covered" style="color:#bbb">Text under the strip.</p>
    <nav class="strip" style="background:#fff"><a class="week" href="/w" style="color:#bbb">WK 08</a></nav>
  </main>`);
  const failures = await scanContrast(page, "nav.strip");
  expect(failures).toEqual([expect.stringMatching(/^violation: a .*contrast.*#bbbbbb/)]);
});

/*
 * A sticky band with a title that an ellipsis cuts by 1px, over a page scrolled under the band, as the top band shows at
 * 1280px when the pill bar takes all the room. Chromium gives such a title two text boxes: the full text and the cut text.
 * The tile under the band ends between the centers of the two boxes, so axe finds a different stack under each box.
 */
async function bandOverScrolledPage(page: Page, titleColor: string) {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.setContent(`<body style="margin:0;background:#fff">
    <header style="position:sticky;top:0;z-index:1;background:#fff;padding:16px">
      <span class="title" style="display:block;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;font:700 16px sans-serif;color:${titleColor}">Cornerstone Fantasy Football League</span>
    </header>
    <main style="height:3000px;padding-top:600px"><div class="tile" style="height:400px;background:#eee"></div></main>
  </body>`);
  await page.evaluate(() => {
    const title = document.querySelector(".title") as HTMLElement;
    const range = document.createRange();
    range.selectNodeContents(title.firstChild as Text);
    title.style.width = `${range.getBoundingClientRect().width - 1}px`;
    const centers = [...range.getClientRects()].map((rect) => (rect.left + rect.right) / 2);
    const tile = document.querySelector(".tile") as HTMLElement;
    tile.style.width = `${(Math.min(...centers) + Math.max(...centers)) / 2}px`;
    window.scrollTo({
      top: tile.getBoundingClientRect().top + window.scrollY - 20,
      behavior: "instant",
    });
  });
}

test("a band title cut by an ellipsis over a scrolled page passes, because its opaque band hides the page under it", async ({
  page,
}) => {
  await bandOverScrolledPage(page, "#111");
  expect(await scanContrast(page)).toEqual([]);
});

test("a faint band title cut by an ellipsis over a scrolled page still fails", async ({ page }) => {
  await bandOverScrolledPage(page, "#bbb");
  expect(await scanContrast(page)).toEqual([
    expect.stringMatching(/^violation: span .*contrast.*#bbbbbb/),
  ]);
});

test("the full axe scan counts the violations and the incomplete items apart, and passes a clean part", async ({
  page,
}) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<html lang="en"><head><title>Axe</title></head><body><main style="background:#fff">
    <section class="part"><button class="bare" style="width:48px;height:48px"></button></section>
    <div style="background:linear-gradient(#000,#fff)"><p class="glow" style="color:#777">Text on a glow.</p></div>
    <section class="clean"><h2 style="color:#111">A clean part</h2><button style="color:#111">Claim</button></section>
  </main></body></html>`);
  const scan = await scanAxe(page);
  expect(scan.violations).toEqual([expect.stringMatching(/^violation: \.bare .*button-name/)]);
  expect(scan.incomplete).toEqual([
    expect.stringMatching(/^incomplete: p color-contrast: .*gradient/),
  ]);
  expect(await scanAxe(page, "section.clean")).toEqual({ violations: [], incomplete: [] });
});

test("openPage sets each theme through the shipped boot script and the server gives 404.html for a missing path", async ({
  page,
}) => {
  const dir = mkdtempSync(join(tmpdir(), "floor-"));
  writeFileSync(
    join(dir, "index.html"),
    `<html class="${DARK_CLASS}"><head><script>${BOOT_SCRIPT}</script></head><body>Home</body></html>`,
  );
  writeFileSync(join(dir, "404.html"), "<html><body>Not found</body></html>");
  const server = await serveDir(dir);
  try {
    await openPage(page, `${server.url}/`, "dark");
    await expect(page.locator("html")).toHaveClass(new RegExp(DARK_CLASS));
    await openPage(page, `${server.url}/`, "light");
    await expect(page.locator("html")).not.toHaveClass(new RegExp(DARK_CLASS));
    const missing = await page.goto(`${server.url}/no/such/page/`);
    expect(missing?.status()).toBe(404);
    await expect(page.locator("body")).toHaveText("Not found");
  } finally {
    await server.close();
    rmSync(dir, { recursive: true });
  }
});

/*
 * Each page below holds an animation that never finishes. A test timeout of 15 s fails a run that hangs, and the cap
 * of openPage is 5 s, so a pass proves that the cap and the finite rule both hold.
 */
const HANG_TIMEOUT = 15_000;

async function openHangPage(page: Parameters<typeof openPage>[0], body: string): Promise<void> {
  const dir = mkdtempSync(join(tmpdir(), "floor-"));
  writeFileSync(
    join(dir, "index.html"),
    `<html><body><div id="box">Box</div><script>${body}</script></body></html>`,
  );
  const server = await serveDir(dir);
  try {
    await openPage(page, `${server.url}/`, "light");
  } finally {
    await server.close();
    rmSync(dir, { recursive: true });
  }
}

test("openPage does not hang on an animation with an end time that is not finite", async ({
  page,
}) => {
  test.setTimeout(HANG_TIMEOUT);
  // A scroll-driven animation has an end time that is not a number, and it stays running.
  await openHangPage(
    page,
    `const box = document.getElementById("box");
     const timeline = new ScrollTimeline({ source: document.documentElement });
     box.animate({ opacity: [0, 1] }, { timeline, fill: "both" });`,
  );
  const ends = await page.evaluate(() =>
    document.getAnimations().map((animation) => animation.effect?.getComputedTiming().endTime),
  );
  expect(ends.some((end) => typeof end !== "number" || !Number.isFinite(end))).toBe(true);
});

test("openPage does not hang on a finite animation that never finishes", async ({ page }) => {
  test.setTimeout(HANG_TIMEOUT);
  await openHangPage(
    page,
    `const animation = document.getElementById("box").animate({ opacity: [0, 1] }, 1000); animation.pause();`,
  );
});
