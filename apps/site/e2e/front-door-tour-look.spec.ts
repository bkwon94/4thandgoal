/**
 * The look of the Tour of the front door on the static export in out/ of the current CLIENT, in WebKit, as Safari runs.
 * It checks the pad and the shape of the hole, the place and the height of the card, the scroll into view, and the follow.
 */
import { type Page, devices, expect, test } from "@playwright/test";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { skipAnnouncements } from "./announcement";
import { serveDir } from "./serve";
import { findOverlap } from "./smoke";
import { skipTour } from "./tour";

const OUT = join(process.cwd(), "out");
// The client build writes the hidden /ask/ route only while the flag front_door is off. Then / is the home page.
const DOOR = existsSync(join(OUT, "ask", "index.html")) ? "/ask/" : "/";
const BO_GIRDS = "6";
const HEADERS = ["Suggestions", "Ask", "Your team", "Menu"];

// The browser of a file is set at its top, because a group cannot pick the browser. Safari runs on WebKit.
test.use({ browserName: "webkit" });

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

type Rect = { x: number; y: number; width: number; height: number };

/* A browser with Your team, a kept passphrase, and no seen key. Each call off the test server fails, because the run
   uses no real API. */
async function openTour(page: Page, theme?: "light" | "dark") {
  await page.route(
    (url) => url.hostname !== "127.0.0.1",
    (route) => route.abort(),
  );
  await page.addInitScript(
    ({ team, theme }) => {
      localStorage.setItem("cpc.passphrase", "test");
      localStorage.setItem("cpc.your-team", team);
      // A kept team lets The Race Announcement open first and cover the page, so the setup marks it seen.
      localStorage.setItem("cpc.announcement.the-race-2026", "seen");
      if (theme) localStorage.setItem("cpc.theme", theme);
    },
    { team: BO_GIRDS, theme },
  );
  await page.goto(`${server.url}${DOOR}`);
  await expect(card(page, "Suggestions")).toBeVisible();
}

/* The stream of a free answer that the API recorded. */
const FREE = readFileSync(join(process.cwd(), "src", "fixtures", "free-answer", "fix.sse"), "utf8");
const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "*",
  "access-control-allow-methods": "POST",
};

/* A browser with Your team, a kept passphrase, and the seen key, so the Tour shows only on a replay. The fake of the API
   port routes each question to a free answer and sends the recorded stream, so the run needs no key of Claude. */
async function openDoorWithFreeAnswer(page: Page) {
  await page.route(
    (url) => url.hostname !== "127.0.0.1",
    (route) => route.abort(),
  );
  await page.route("**/clients/*/ask", (route) =>
    route.fulfill({
      status: route.request().method() === "OPTIONS" ? 204 : 200,
      headers: CORS,
      contentType: "application/json",
      body: JSON.stringify({
        route: "free",
        line: null,
        topic: null,
        team: null,
        closest: [],
        suggestion: null,
      }),
    }),
  );
  await page.route("**/clients/*/ask/free", (route) =>
    route.request().method() === "OPTIONS"
      ? route.fulfill({ status: 204, headers: CORS })
      : route.fulfill({
          status: 200,
          headers: {
            ...CORS,
            "access-control-expose-headers": "*",
            "x-vercel-ai-ui-message-stream": "v1",
          },
          contentType: "text/event-stream",
          body: FREE,
        }),
  );
  await skipTour(page);
  await skipAnnouncements(page);
  await page.addInitScript((team) => {
    localStorage.setItem("cpc.passphrase", "test");
    localStorage.setItem("cpc.your-team", team);
  }, BO_GIRDS);
  await page.goto(`${server.url}${DOOR}`);
}

const card = (page: Page, name: string) => page.getByRole("dialog", { name });

async function rectOf(page: Page, selector: string): Promise<Rect> {
  return page.locator(selector).evaluate((el) => {
    const rect = el.getBoundingClientRect();
    return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
  });
}

/* The hole, read once it rests: two reads one frame apart that agree. */
async function restingHole(page: Page) {
  const read = () =>
    page.locator("[data-tour-hole]").evaluate((el) => {
      const rect = el.getBoundingClientRect();
      return {
        x: rect.x,
        y: rect.y,
        width: rect.width,
        height: rect.height,
        radius: parseFloat(getComputedStyle(el).borderTopLeftRadius),
      };
    });
  let last = await read();
  await expect
    .poll(async () => {
      const now = await read();
      const still =
        Math.abs(now.x - last.x) < 0.5 &&
        Math.abs(now.y - last.y) < 0.5 &&
        Math.abs(now.width - last.width) < 0.5;
      last = now;
      return still;
    })
    .toBe(true);
  return last;
}

/* The part of the control of each Stop that the eye sees, by the rule of the decision ticket 02 of the Tour, "What a Stop
   looks like". The ask box has its own fill and border, so it counts whole. The Suggestions row counts its chips, inside
   the screen less 8 px. The team switch counts its avatar, its name, and its mark. The menu button counts only its icon. The pill bar counts its links. */
async function visualBox(page: Page, header: string): Promise<Rect> {
  return page.evaluate((header) => {
    const union = (rects: DOMRect[]) => {
      const left = Math.min(...rects.map((r) => r.left));
      const top = Math.min(...rects.map((r) => r.top));
      const right = Math.max(...rects.map((r) => r.right));
      const bottom = Math.max(...rects.map((r) => r.bottom));
      return { x: left, y: top, width: right - left, height: bottom - top };
    };
    const visible = (el: Element) => (el as HTMLElement).checkVisibility?.() ?? true;
    if (header === "Ask")
      return union([document.querySelector('form[aria-label="Ask"]')!.getBoundingClientRect()]);
    if (header === "Suggestions") {
      const chips = [
        ...document.querySelectorAll('[role="group"][aria-label="Suggestions"] > button'),
      ].map((el) => el.getBoundingClientRect());
      const box = union(chips);
      const left = Math.max(8, box.x);
      const right = Math.min(window.innerWidth - 8, box.x + box.width);
      return { x: left, y: box.y, width: right - left, height: box.height };
    }
    if (header === "Your team") {
      const button = document.querySelector('button[aria-label^="Your team:"]')!;
      return union([...button.children].filter(visible).map((el) => el.getBoundingClientRect()));
    }
    const menu = [...document.querySelectorAll('button[aria-label="Open the menu"]')].find(visible);
    if (menu)
      return union([menu.querySelector("svg:not([style*='none'])")!.getBoundingClientRect()]);
    const bar = document.querySelector('nav[aria-label="Site menu"]')!;
    return union([...bar.querySelectorAll("a")].map((el) => el.getBoundingClientRect()));
  }, header);
}

async function goTo(page: Page, header: string) {
  for (const name of HEADERS.slice(0, HEADERS.indexOf(header))) {
    await card(page, name).getByRole("button", { name: "Next" }).click();
  }
  await expect(card(page, header)).toBeVisible();
}

/* Each Stop in order: run the check on the Stop, then tap Next to go on. Stop 4 shows Done, so the walk ends there. */
async function eachStop(page: Page, check: (header: string) => Promise<void>) {
  for (const [index, header] of HEADERS.entries()) {
    await expect(card(page, header)).toBeVisible();
    await check(header);
    if (index < HEADERS.length - 1)
      await card(page, header).getByRole("button", { name: "Next" }).click();
  }
}

const overlap = (a: Rect, b: Rect) =>
  a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height;

for (const width of [375, 1280]) {
  test(`the hole pad is even on each side of the visual box, a circle on the menu button and a pill on each other control, at ${width} px (AT-14)`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 800 });
    await openTour(page);
    await eachStop(page, async (header) => {
      const hole = await restingHole(page);
      const box = await visualBox(page, header);
      const pad = box.height < 28 ? 10 : 6;
      const sides = {
        left: box.x - hole.x,
        top: box.y - hole.y,
        right: hole.x + hole.width - (box.x + box.width),
        bottom: hole.y + hole.height - (box.y + box.height),
      };
      // The evidence of AT-14 is the measured rect of each control and each hole, so the log prints them.
      console.log(
        `AT-14 ${width} px ${header}: control ${JSON.stringify(box)}, hole ${JSON.stringify(hole)}, pads ${JSON.stringify(sides)}, expected pad ${pad}`,
      );
      for (const [side, value] of Object.entries(sides)) {
        expect(
          Math.abs(value - pad),
          `${header}: the ${side} pad is ${value}px, not ${pad}px`,
        ).toBeLessThanOrEqual(1);
      }
      expect(hole.radius, `${header}: the hole is round at its ends`).toBeGreaterThanOrEqual(
        hole.height / 2 - 1,
      );
      const menuButton = width < 1000 && header === "Menu";
      if (menuButton)
        expect(
          Math.abs(hole.width - hole.height),
          "the hole on the menu button is a circle",
        ).toBeLessThanOrEqual(1);
      else expect(hole.width, `${header}: the hole is a pill`).toBeGreaterThan(hole.height);
    });
  });

  test(`the card height is the same at all four Stops at ${width} px (AT-17)`, async ({ page }) => {
    await page.setViewportSize({ width, height: 800 });
    await openTour(page);
    const heights: number[] = [];
    await eachStop(page, async () => {
      await restingHole(page);
      heights.push((await rectOf(page, "[data-tour-card]")).height);
    });
    console.log(`AT-17 ${width} px card heights at Stops 1 to 4: ${heights.join(", ")}`);
    for (const height of heights)
      expect(
        Math.abs(height - heights[0]),
        `the heights are ${heights.join(", ")}`,
      ).toBeLessThanOrEqual(1);
  });
}

/* The four viewports of the iPhone rule: an iPhone in Safari, an iPad in portrait and in landscape, and a desktop. */
const VIEWPORTS = [
  {
    name: "iPhone 390x660",
    use: { ...devices["iPhone 15"], viewport: { width: 390, height: 660 } },
  },
  {
    name: "iPad 810x980",
    use: { ...devices["iPad (gen 7)"], viewport: { width: 810, height: 980 } },
  },
  {
    name: "iPad 1080x740",
    use: { ...devices["iPad (gen 7) landscape"], viewport: { width: 1080, height: 740 } },
  },
  { name: "desktop 1280x800", use: { viewport: { width: 1280, height: 800 } } },
];

for (const viewport of VIEWPORTS) {
  test.describe(viewport.name, () => {
    const { defaultBrowserType: _browser, ...use } = viewport.use as typeof viewport.use & {
      defaultBrowserType?: string;
    };
    test.use(use);

    test(`the card does not overlap its control at any Stop (AT-16)`, async ({ page }) => {
      await openTour(page);
      await eachStop(page, async (header) => {
        await restingHole(page);
        const cardRect = await rectOf(page, "[data-tour-card]");
        const control = await rectOf(page, "[data-tour-target]");
        // The evidence of AT-16 is the rects and a screenshot of each Stop on each viewport, so the test logs and saves them.
        console.log(
          `AT-16 ${viewport.name} ${header}: card ${JSON.stringify(cardRect)}, control ${JSON.stringify(control)}, overlap ${overlap(cardRect, control)}`,
        );
        // The copy of the card cross-fades after the hole rests, so the shot waits for the swap to end.
        await page.waitForTimeout(1000);
        await page.screenshot({
          path: test
            .info()
            .outputPath(
              `${viewport.name.split(" ").at(-1)}-${header.replace(" ", "-").toLowerCase()}.png`,
            ),
        });
        expect(
          overlap(cardRect, control),
          `${header}: the card ${JSON.stringify(cardRect)} covers its control ${JSON.stringify(control)}`,
        ).toBe(false);
        const size = page.viewportSize()!;
        expect(cardRect.y, `${header}: the card top is on the screen`).toBeGreaterThanOrEqual(0);
        expect(
          cardRect.y + cardRect.height,
          `${header}: the card bottom is on the screen`,
        ).toBeLessThanOrEqual(size.height);
      });
    });
  });
}

test.describe("iPhone 390x660", () => {
  const { defaultBrowserType: _browser, ...iphone } = devices["iPhone 15"];
  test.use({ ...iphone, viewport: { width: 390, height: 660 } });

  test("each control is inside the visual viewport when its Stop shows, from a page at its top (AT-18)", async ({
    page,
  }) => {
    await openTour(page);
    expect(await page.evaluate(() => window.scrollY)).toBe(0);
    await eachStop(page, async (header) => {
      await restingHole(page);
      const control = await rectOf(page, "[data-tour-target]");
      const view = await page.evaluate(() => ({
        width: window.visualViewport!.width,
        height: window.visualViewport!.height,
      }));
      console.log(
        `AT-18 ${header}: control ${JSON.stringify(control)}, visual viewport ${JSON.stringify(view)}`,
      );
      expect(control.x, `${header}: left edge`).toBeGreaterThanOrEqual(-1);
      expect(control.y, `${header}: top edge`).toBeGreaterThanOrEqual(-1);
      expect(
        control.y + control.height,
        `${header}: bottom edge in ${view.height}`,
      ).toBeLessThanOrEqual(view.height + 1);
      // The Suggestions row bleeds to both edges and scrolls sideways, so its box is the width of the screen.
      expect(
        control.x + control.width,
        `${header}: right edge in ${view.width}`,
      ).toBeLessThanOrEqual(view.width + 1);
    });
  });

  test("the overlap check of the smoke run finds no overlap when each Stop shows over the first answer", async ({
    page,
  }) => {
    await openDoorWithFreeAnswer(page);
    await page.getByRole("textbox", { name: "Ask a question" }).fill("who has the best roster");
    await page.getByRole("button", { name: "Send" }).click();
    await expect(
      page
        .getByRole("article", { name: "who has the best roster" })
        .getByRole("status")
        .getByText("Checked"),
    ).toBeVisible();
    await page.getByRole("button", { name: "Open the menu" }).click();
    await page.getByRole("button", { name: "Show the tour" }).click();
    await eachStop(page, async (header) => {
      // The copy of the card cross-fades after the hole rests, so the check polls until the fade ends.
      await expect
        .poll(() => findOverlap(page), { message: `${header}: the overlap check of the smoke run` })
        .toBeNull();
    });
  });

  test("after a turn of the phone from 390x660 to 660x390 at Stop 2, the hole stays on the ask box (AT-19)", async ({
    page,
  }) => {
    await openTour(page);
    await goTo(page, "Ask");
    // The evidence of AT-19 is the rects before and after, and a screenshot at each size, so the test logs and saves them.
    console.log(
      `AT-19 before at 390x660: hole ${JSON.stringify(await restingHole(page))}, ask box ${JSON.stringify(await rectOf(page, 'form[aria-label="Ask"]'))}`,
    );
    await page.waitForTimeout(1000);
    await page.screenshot({ path: test.info().outputPath("390x660.png") });
    await page.setViewportSize({ width: 660, height: 390 });
    await expect
      .poll(async () => {
        const hole = await restingHole(page);
        const ask = await rectOf(page, 'form[aria-label="Ask"]');
        return Math.max(
          Math.abs(hole.x + hole.width / 2 - (ask.x + ask.width / 2)),
          Math.abs(hole.y + hole.height / 2 - (ask.y + ask.height / 2)),
        );
      })
      .toBeLessThanOrEqual(2);
    console.log(
      `AT-19 after at 660x390: hole ${JSON.stringify(await restingHole(page))}, ask box ${JSON.stringify(await rectOf(page, 'form[aria-label="Ask"]'))}`,
    );
    await page.waitForTimeout(1000);
    await page.screenshot({ path: test.info().outputPath("660x390.png") });
  });
});

for (const theme of ["light", "dark"] as const) {
  test(`Next and Done fill with the accent token and use the on-dark text in the ${theme} theme (AT-22)`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 660 });
    await page.emulateMedia({ colorScheme: theme });
    await openTour(page, theme);
    // The token colors, read from a probe that paints each token, so the check compares two computed colors.
    const tokens = await page.evaluate(() => {
      const probe = document.createElement("div");
      probe.style.backgroundColor = "var(--color-accent)";
      probe.style.color = "var(--color-on-dark)";
      document.body.append(probe);
      const style = getComputedStyle(probe);
      const colors = { fill: style.backgroundColor, text: style.color };
      probe.remove();
      return colors;
    });
    const colorsOf = (name: string, button: string) =>
      card(page, name)
        .getByRole("button", { name: button })
        .evaluate((el) => ({
          fill: getComputedStyle(el).backgroundColor,
          text: getComputedStyle(el).color,
        }));
    // The evidence of AT-22 is the computed colors in each theme, so the log prints them.
    const next = await colorsOf("Suggestions", "Next");
    console.log(
      `AT-22 ${theme}: tokens accent and on-dark ${JSON.stringify(tokens)}, Next ${JSON.stringify(next)}`,
    );
    expect(next).toEqual(tokens);
    await goTo(page, "Menu");
    const done = await colorsOf("Menu", "Done");
    console.log(`AT-22 ${theme}: Done ${JSON.stringify(done)}`);
    expect(done).toEqual(tokens);
  });
}
