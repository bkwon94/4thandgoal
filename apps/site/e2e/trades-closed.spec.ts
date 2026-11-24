/**
 * The closed analyzer page of a build after the Lock, in WebKit: the line, the one Home link, and the same page for each old
 * link of the analyzer, at 375, 768, and 1280 px in both themes, then the iPhone 15. Run it on the export of cpc built with
 * the real clock or a BUILD_NOW after the Lock: CLIENT=cpc BUILD_NOW=2026-11-24T00:00:00-05:00 pnpm build
 */
import { devices, expect, test } from "@playwright/test";
import { join } from "node:path";
import type { Theme } from "@cpc/design/lib/theme";
import { openPage } from "./floor";
import { serveDir } from "./serve";
import { findOverlap } from "./smoke";

const OUT = join(process.cwd(), "out");
const LINE = "The trade deadline has passed. Trades open again next season.";
// The old links of the analyzer: the page itself, a prefill link, and a Finder link. Each gives the same page.
const LINKS = [
  "/analyze/",
  "/analyze/?team=3&with=6&give=5045&get=8151",
  "/analyze/?mode=find",
] as const;

// The browser of a file is set at its top, because a group cannot pick the browser. Safari runs on WebKit.
test.use({ browserName: "webkit", reducedMotion: "reduce" });

/* The iPhone 15 with no browser of its own, because a group cannot pick the browser. */
const { defaultBrowserType: _phone, ...IPHONE } = devices["iPhone 15"];

const VIEWPORTS = [
  { name: "375", use: { viewport: { width: 375, height: 812 } } },
  { name: "768", use: { viewport: { width: 768, height: 1024 } } },
  { name: "1280", use: { viewport: { width: 1280, height: 800 } } },
  { name: "iPhone 15 390x660", use: { ...IPHONE, viewport: { width: 390, height: 660 } } },
] as const;

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server?.close();
});

for (const viewport of VIEWPORTS) {
  test.describe(viewport.name, () => {
    test.use(viewport.use);
    for (const theme of ["light", "dark"] as const satisfies readonly Theme[]) {
      for (const link of LINKS) {
        test(`${link} shows the closed page, ${theme} (AT-3, AT-4, AT-5)`, async ({
          page,
        }, info) => {
          await openPage(page, `${server.url}${link}`, theme);
          const main = page.getByRole("main");
          await expect(main.getByText(LINE)).toBeVisible();
          const home = main.getByRole("link");
          await expect(home).toHaveCount(1);
          await expect(home).toHaveText("Home");
          await expect(home).toHaveAttribute("href", "/");
          // The page holds no trade form and no switch of the two modes.
          await expect(page.getByText("Grade a trade")).toHaveCount(0);
          await expect(page.getByRole("button", { name: /Grade the Trade/ })).toHaveCount(0);
          await page.screenshot({
            path: info.outputPath(`trades-closed-${theme}.png`),
            fullPage: true,
          });
          const wide = await page.evaluate(
            () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
          );
          expect(wide, "the page scrolls sideways").toBe(false);
          expect(await findOverlap(page)).toBeNull();
        });
      }
    }
  });
}

test("a browser clock before the Lock still shows the closed page and no Trade Analyzer in the menu (AT-26)", async ({
  page,
}) => {
  // The menu button shows only below the desktop width, so the test runs at the phone size.
  await page.setViewportSize({ width: 390, height: 660 });
  // The build decides, not the browser: 20:00 Eastern on Mon 2026-11-23 is before the Lock.
  await page.clock.setFixedTime(new Date("2026-11-23T20:00:00-05:00"));
  await openPage(page, `${server.url}/analyze/`, "dark");
  await expect(page.getByRole("main").getByText(LINE)).toBeVisible();
  await page.getByRole("button", { name: "Open the menu" }).click();
  await expect(page.getByRole("dialog").getByText("Trade Analyzer")).toHaveCount(0);
});
