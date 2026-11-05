/**
 * Proves each rule of the readability floor on a small real page in Chromium, so the floor fails on what it must fail.
 * Each page is plain HTML that the browser lays out, so the scans measure real boxes, sizes, and colors.
 */
import { BOOT_SCRIPT, DARK_CLASS } from "@cpc/design/lib/theme";
import { expect, test } from "@playwright/test";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { openPage, scanContrast, scanScroll, scanTargets, scanText } from "./floor";
import { serveDir } from "./serve";

const PHONE = { width: 390, height: 844 };

test("prose under 16px fails and names the element and the size", async ({ page }) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<main><p class="blurb" style="font-size:14px">A short blurb of the week.</p></main>`);
  const scan = await scanText(page);
  expect(scan.failures).toEqual([expect.stringMatching(/p\.blurb .*14px.*prose.*16px/)]);
});

test("other text under 11px fails, 11px passes, and the scan counts each tier", async ({ page }) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<main>
    <span class="eyebrow" style="font-size:11px">Week 8</span>
    <span class="dock" style="font-size:10px">Home</span>
    <div data-prose style="font-size:16px">A recap with a <b>bold</b> word.</div>
    <p style="font-size:16px">A blurb.</p>
  </main>`);
  const scan = await scanText(page);
  expect(scan.failures).toEqual([expect.stringMatching(/span\.dock "Home" is 10px.*other text.*11px/)]);
  expect(scan).toMatchObject({ prose: 3, other: 2 });
});

test("a link or button under 44px fails, and a link inside prose is exempt and listed", async ({ page }) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<main>
    <a class="row" href="/a" style="display:block;height:48px">A whole row</a>
    <button class="close" style="width:30px;height:30px">x</button>
    <p style="font-size:16px">Read the <a class="inline" href="/b">manager page</a> next.</p>
  </main>`);
  const scan = await scanTargets(page);
  expect(scan.failures).toEqual([expect.stringMatching(/button\.close "x" is 30x30px, under the tap floor of 44px/)]);
  expect(scan.exempt).toEqual([expect.stringMatching(/a\.inline "manager page"/)]);
});

test("a sideways scroll at 390px fails and names the widest element, and a box that scrolls itself passes", async ({ page }) => {
  await page.setViewportSize(PHONE);
  await page.setContent(`<body style="margin:0">
    <div style="overflow-x:auto"><table style="width:900px"><tr><td>A wide table in its own box</td></tr></table></div>
  </body>`);
  expect(await scanScroll(page)).toEqual([]);

  await page.setContent(`<body style="margin:0"><div class="strip" style="width:500px">A strip of weeks</div></body>`);
  expect(await scanScroll(page)).toEqual([expect.stringMatching(/scrolls sideways: 500px wide in 390px.*div\.strip/)]);
});

test("axe color-contrast fails on a violation and on an incomplete result, and passes a clear pair", async ({ page }) => {
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

test("openPage sets each theme through the shipped boot script and the server gives 404.html for a missing path", async ({
  page,
}) => {
  const dir = mkdtempSync(join(tmpdir(), "floor-"));
  writeFileSync(join(dir, "index.html"), `<html class="${DARK_CLASS}"><head><script>${BOOT_SCRIPT}</script></head><body>Home</body></html>`);
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
