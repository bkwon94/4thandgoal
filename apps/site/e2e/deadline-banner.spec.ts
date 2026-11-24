/**
 * The Deadline banner on the static export in out/ of the current CLIENT, in WebKit, as Safari runs, with a fixed clock.
 * It checks the text of each phase, the band that grows to fit, the even pad, the press, the sheet, and no overlap.
 */
import { type Page, devices, expect, test } from "@playwright/test";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
const CLIENT = process.env.CLIENT ?? "cpc";
// The client build writes the hidden /ask/ route only while the flag front_door is off. Then / is the home page.
const DOOR = existsSync(join(OUT, "ask", "index.html")) ? "/ask/" : "/";
const BO_GIRDS = "6";

/* The fixed clocks of the acceptance tests, in Eastern time. The Lock of cpc is 00:00 Eastern on Tue 2026-11-24. */
const OPEN = "2026-11-21T09:55:00-05:00";
const LAST_HOURS = "2026-11-23T21:18:50-05:00";
const CLOSED = "2026-11-24T00:00:01-05:00";
const ENDED = "2026-11-25T00:00:01-05:00";

/* The recorded answers of the Trade Wire route, the fixed inputs of the tests that open the sheet. Week 11 of cpc held
   no trade when the route read Sleeper leg 11, so the route answered this empty list. The answer of leg 9 holds two
   real trades, for a test that needs a trade. */
type WireAnswer = { leg: number; trades: unknown[] };
const WIRE_EMPTY: WireAnswer = { leg: 11, trades: [] };
const WIRE_TWO: WireAnswer = JSON.parse(
  readFileSync(
    join(
      process.cwd(),
      "..",
      "..",
      "packages",
      "analyzer",
      "site",
      "deadline",
      "fixtures",
      "trade-wire-cpc-week-9.json",
    ),
    "utf8",
  ),
);
const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "*",
  "access-control-allow-methods": "GET",
};

// The browser of a file is set at its top, because a group cannot pick the browser. Safari runs on WebKit.
test.use({ browserName: "webkit", reducedMotion: "no-preference" });

/* The iPhone 15 with no browser of its own, because a group cannot pick the browser. The file runs WebKit. */
const { defaultBrowserType: _browser, ...IPHONE } = devices["iPhone 15"];

/* The iPhone 15 at 390 by 660, the iPad upright and on its side, and the desktop. */
const VIEWPORTS = [
  { name: "iPhone 15 390x660", use: { ...IPHONE, viewport: { width: 390, height: 660 } } },
  { name: "iPad 810x980", use: { viewport: { width: 810, height: 980 } } },
  { name: "iPad 1080x740", use: { viewport: { width: 1080, height: 740 } } },
  { name: "desktop 1280x800", use: { viewport: { width: 1280, height: 800 } } },
] as const;

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

type Rect = { x: number; y: number; width: number; height: number };

/* The front door at the clock `time`, in the theme `theme`. A fixed clock stands still, so a slow load never moves the
   seconds. A clock that ticks starts at `time` and runs, so a test can move it on. Each call off the test server fails,
   because the run uses no real API, except the Trade Wire route. That route gives the recorded answer `wire`, or fails
   when `wire` is "fail". It answers only after `gate` resolves, so a test can look at the banner before the first read.
   The setup marks the Tour and the Announcement seen, unless the test asks for the
   Tour, so no card covers the banner. */
async function openAt(
  page: Page,
  time: string,
  {
    theme = "light",
    path = DOOR,
    tour = false,
    ticks = false,
    wire = WIRE_EMPTY,
    gate = Promise.resolve(),
  }: {
    theme?: "light" | "dark";
    path?: string;
    tour?: boolean;
    ticks?: boolean;
    wire?: WireAnswer | "fail";
    gate?: Promise<void>;
  } = {},
) {
  await page.route(
    (url) => url.hostname !== "127.0.0.1",
    (route) => route.abort(),
  );
  // A route added later takes the call first, so this one wins over the abort above.
  await page.route(/\/deadline\/trades$/, async (route) => {
    if (route.request().method() === "OPTIONS")
      return route.fulfill({ status: 204, headers: CORS });
    await gate;
    if (wire === "fail") return route.abort();
    return route.fulfill({
      status: 200,
      headers: CORS,
      contentType: "application/json",
      body: JSON.stringify(wire),
    });
  });
  if (ticks) await page.clock.install({ time: new Date(time) });
  else await page.clock.setFixedTime(new Date(time));
  await page.addInitScript(
    ({ theme, team, tour }) => {
      localStorage.setItem("cpc.theme", theme);
      localStorage.setItem("cpc.passphrase", "test");
      localStorage.setItem("cpc.your-team", team);
      localStorage.setItem("cpc.announcement.the-race-2026", "seen");
      if (!tour) localStorage.setItem("cpc.tour-seen", "1");
    },
    { theme, team: BO_GIRDS, tour },
  );
  await page.goto(`${server.url}${path}`);
}

const banner = (page: Page) => page.locator("[data-deadline-banner]");
const trigger = (page: Page) => page.getByRole("button", { name: /^Open the Trade Wire/ });

async function rectOf(page: Page, selector: string): Promise<Rect> {
  return page
    .locator(selector)
    .first()
    .evaluate((el) => {
      const rect = el.getBoundingClientRect();
      return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
    });
}

const overlap = (a: Rect, b: Rect) =>
  a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height;

/* No horizontal scroll, the banner inside the band and under its row, and the band height token equal to the band. */
async function expectFits(page: Page) {
  // The banner measures itself with a ResizeObserver, which reports after a layout. A change of phase swaps the
  // placeholder for a banner of another height, so the check tries again until the observer has reported.
  await expect(async () => {
    const fit = await page.evaluate(() => {
      const header = document.querySelector("header")!;
      const row = header.firstElementChild!.getBoundingClientRect();
      const strip = document.querySelector("[data-deadline-banner]")!.getBoundingClientRect();
      const probe = document.createElement("div");
      probe.style.height = "var(--spacing-band-height)";
      document.body.append(probe);
      const token = probe.getBoundingClientRect().height;
      probe.remove();
      const bannerToken = parseFloat(
        document.documentElement.style.getPropertyValue("--deadline-banner-h"),
      );
      return {
        scroll: document.documentElement.scrollWidth - window.innerWidth,
        rowBottom: row.bottom,
        stripTop: strip.top,
        stripBottom: strip.bottom,
        stripWidth: strip.width,
        stripHeight: strip.height,
        bannerToken,
        headerBottom: header.getBoundingClientRect().bottom,
        headerHeight: header.getBoundingClientRect().height,
        token,
        width: window.innerWidth,
      };
    });
    console.log(`fit: ${JSON.stringify(fit)}`);
    expect(fit.scroll, "the page scrolls sideways").toBeLessThanOrEqual(0);
    expect(fit.stripTop, "the banner overlaps the row of the band").toBeGreaterThanOrEqual(
      fit.rowBottom - 0.5,
    );
    expect(fit.stripBottom).toBeLessThanOrEqual(fit.headerBottom + 0.5);
    expect(fit.stripWidth).toBeLessThanOrEqual(fit.width);
    expect(
      Math.abs(fit.token - fit.headerHeight),
      "the band height token does not hold the banner",
    ).toBeLessThanOrEqual(0.01);
    // The banner token keeps the fraction of a pixel, so a part that sticks at the band height sits flush with the band.
    expect(
      Math.abs(fit.bannerToken - fit.stripHeight),
      "the banner token rounds the height of the banner",
    ).toBeLessThanOrEqual(0.01);
  }).toPass({ timeout: 2000 });
}

for (const viewport of VIEWPORTS) {
  test.describe(viewport.name, () => {
    test.use(viewport.use);
    test.skip(CLIENT !== "cpc", "Only cpc has a Lock.");

    for (const theme of ["light", "dark"] as const) {
      test(`${theme}: the banner shows TRADE DEADLINE over the countdown, fits the band, and ticks (AT-1, AT-2)`, async ({
        page,
      }, info) => {
        await openAt(page, OPEN, { theme, ticks: true });
        await expect(banner(page).locator("[data-deadline-eyebrow]")).toHaveText("TRADE DEADLINE", {
          useInnerText: true,
        });
        await expect(banner(page).locator("[data-deadline-countdown]")).toHaveText("~2d 14h 05m");
        await expectFits(page);
        await page.locator("header").screenshot({ path: info.outputPath(`open-${theme}.png`) });
        await page.clock.runFor(60_000);
        await expect(banner(page).locator("[data-deadline-countdown]")).toHaveText("~2d 14h 04m");
      });

      test(`${theme}: the banner has even padding and one left edge (AT-8)`, async ({ page }) => {
        await openAt(page, OPEN, { theme });
        await expect(banner(page).locator("[data-deadline-countdown]")).toHaveText("~2d 14h 05m");
        const box = await page.evaluate(() => {
          const rect = (selector: string) =>
            document.querySelector(selector)!.getBoundingClientRect();
          const button = rect("[data-deadline-banner] button");
          const eyebrow = rect("[data-deadline-eyebrow]");
          const countdown = rect("[data-deadline-countdown]");
          const border = parseFloat(
            getComputedStyle(document.querySelector("[data-deadline-banner] button")!)
              .borderTopWidth,
          );
          return {
            top: eyebrow.top - button.top - border,
            bottom: button.bottom - countdown.bottom,
            eyebrowX: eyebrow.left,
            countdownX: countdown.left,
          };
        });
        console.log(`AT-8 ${viewport.name} ${theme}: ${JSON.stringify(box)}`);
        expect(Math.abs(box.top - box.bottom)).toBeLessThanOrEqual(1);
        expect(Math.abs(box.eyebrowX - box.countdownX)).toBeLessThanOrEqual(0.5);
      });

      test(`${theme}: the last hours take the accent fill and show seconds (AT-3)`, async ({
        page,
      }) => {
        await openAt(page, LAST_HOURS, { theme });
        await expect(banner(page).locator("[data-deadline-countdown]")).toHaveText("~2h 41m 10s");
        const fill = await page.evaluate(() => {
          const probe = document.createElement("div");
          probe.style.background = "var(--color-accent)";
          document.body.append(probe);
          const accent = getComputedStyle(probe).backgroundColor;
          probe.remove();
          return {
            accent,
            banner: getComputedStyle(document.querySelector("[data-deadline-banner] button")!)
              .backgroundColor,
          };
        });
        console.log(`AT-3 ${viewport.name} ${theme}: ${JSON.stringify(fill)}`);
        expect(fill.banner).toBe(fill.accent);
        await expectFits(page);
      });

      test(`${theme}: the banner says the trade deadline has passed, with Final, after the Lock (AT-9)`, async ({
        page,
      }) => {
        await openAt(page, CLOSED, { theme });
        await expect(trigger(page)).toContainText(
          "The trade deadline has passed. Good luck in the playoffs.",
        );
        await expect(trigger(page)).toContainText("Final");
        await expectFits(page);
      });
    }

    test("the banner is one button named Open the Trade Wire, and it opens the Trade Wire sheet", async ({
      page,
    }) => {
      // The route holds its answer until the name before the first read is checked.
      let answer = () => {};
      const gate = new Promise<void>((resolve) => (answer = resolve));
      await openAt(page, OPEN, { gate });
      await expect(trigger(page)).toHaveCount(1);
      await expect(
        page.getByRole("button", { name: "Open the Trade Wire", exact: true }),
      ).toBeVisible();
      answer();
      await expect(
        page.getByRole("button", { name: "Open the Trade Wire, 0 new trades", exact: true }),
      ).toBeVisible();
      await trigger(page).click();
      const sheet = page.getByRole("dialog", { name: "Trade Wire" });
      await expect(sheet).toBeVisible();
      await expect(sheet).toContainText("No trades yet this week.");
      await expect(sheet.getByText(/^Trade deadline ~2d 14h 05m$/i)).toBeVisible();
    });

    test("the badge counts the trades of the recorded answer, and the sheet lists them", async ({
      page,
    }) => {
      await openAt(page, OPEN, { wire: WIRE_TWO });
      await expect(
        page.getByRole("button", { name: "Open the Trade Wire, 2 new trades", exact: true }),
      ).toBeVisible();
      await expect(banner(page).locator("[data-deadline-badge]")).toHaveText("2 new");
      await trigger(page).click();
      const sheet = page.getByRole("dialog", { name: "Trade Wire" });
      await expect(sheet.locator("[data-trade]")).toHaveCount(2);
      await expect(sheet).toContainText("Puka Deez... gets");
      await expect(sheet).toContainText("NFC Least gets");
      await expect(sheet).not.toContainText("The last update failed.");
    });

    test("a failed read shows the note of the failure in the sheet", async ({ page }) => {
      await openAt(page, OPEN, { wire: "fail" });
      await trigger(page).click();
      const sheet = page.getByRole("dialog", { name: "Trade Wire" });
      await expect(sheet).toContainText("The last update failed.");
      await expect(sheet.locator("[data-wire-empty]")).toHaveCount(0);
    });

    test("the banner content sinks to 0.98 over 150 ms on a press (AT-7)", async ({ page }) => {
      await openAt(page, OPEN);
      await expect(banner(page).locator("[data-deadline-countdown]")).toHaveText("~2d 14h 05m");
      const box = await rectOf(page, "[data-deadline-banner] button");
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await page.mouse.down();
      // The press sets :active at once, but WebKit starts the scale transition only at its next rendering update. A
      // loaded headless WebKit on Linux can hold that update for more than 700 ms, and the transition stays pending at
      // scale 1. So the test waits until the transition of the press ends, not for a fixed time. With no press, the
      // grid has no transition, and the read below gives scale 1.
      const press = await page.locator("[data-deadline-grid]").evaluate(async (el) => {
        await Promise.all(el.getAnimations().map((animation) => animation.finished));
        const style = getComputedStyle(el);
        return {
          transform: style.transform,
          scale: style.scale,
          duration: style.transitionDuration,
          property: style.transitionProperty,
        };
      });
      await page.mouse.up();
      console.log(`AT-7 ${viewport.name}: ${JSON.stringify(press)}`);
      expect(press.duration.split(",")[0].trim()).toBe("0.15s");
      // Tailwind 4 writes the scale with the scale property, so the transform stays none.
      expect(press.scale === "0.98" || press.transform.startsWith("matrix(0.98")).toBe(true);
    });

    test("reduced motion leaves no running animation in the banner (AT-4)", async ({ page }) => {
      await page.emulateMedia({ reducedMotion: "reduce" });
      await openAt(page, LAST_HOURS);
      await expect(banner(page).locator("[data-deadline-countdown]")).toHaveText("~2h 41m 10s");
      const running = await banner(page).evaluate(
        (el) =>
          el
            .getAnimations({ subtree: true })
            .filter((animation) => animation.playState === "running").length,
      );
      console.log(`AT-4 ${viewport.name}: running animations ${running}`);
      expect(running).toBe(0);
    });

    test("Deadline week ends by itself one day after the Lock (AT-10)", async ({ page }) => {
      await openAt(page, ENDED);
      await expect(page.locator("header")).toBeVisible();
      await expect(banner(page)).toHaveCount(0);
      await page.goto(`${server.url}/analyze/`);
      await expect(page.locator("header")).toBeVisible();
      await expect(banner(page)).toHaveCount(0);
    });
  });
}

test.describe("norcal", () => {
  test.use(VIEWPORTS[0].use);
  test.skip(CLIENT !== "norcal", "Run with CLIENT=norcal on the norcal export.");

  test("Norcal has no Deadline week (AT-11)", async ({ page }) => {
    await openAt(page, OPEN);
    await expect(page.locator("header")).toBeVisible();
    await expect(banner(page)).toHaveCount(0);
  });
});

test.describe("the Tour", () => {
  test.use(VIEWPORTS[0].use);
  test.skip(CLIENT !== "cpc", "Only cpc has a Lock.");

  test("the front door Tour still shows in full on the first visit, with no overlap by the banner", async ({
    page,
  }) => {
    await openAt(page, OPEN, { tour: true });
    const card = page.getByRole("dialog", { name: "Suggestions" });
    await expect(card).toBeVisible();
    await expect(banner(page).locator("[data-deadline-countdown]")).toHaveText("~2d 14h 05m");
    const cardRect = await rectOf(page, "[data-tour-card]");
    const stripRect = await rectOf(page, "[data-deadline-banner]");
    const size = page.viewportSize()!;
    console.log(`Tour card ${JSON.stringify(cardRect)}, banner ${JSON.stringify(stripRect)}`);
    expect(overlap(cardRect, stripRect)).toBe(false);
    expect(cardRect.y).toBeGreaterThanOrEqual(0);
    expect(cardRect.y + cardRect.height).toBeLessThanOrEqual(size.height);
  });
});
