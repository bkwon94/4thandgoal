/**
 * The hero scene of the latest week page on the static export in out/ of the current CLIENT, in Chromium.
 * It checks what jsdom cannot: the pixels of the lights, the settle, the loop at rest, a tap, a slide, a swipe, and the hint.
 */
import { DARK_CLASS, THEME_KEY, type Theme } from "@cpc/design/lib/theme";
import { type HeroScene, SCENE_PADDING, type ScenePoint, nearestLight, placeLights } from "@cpc/design/parts/scene-math";
import { matchupScene } from "@cpc/week/parts/matchup-scene";
import { expect, test, type Page } from "@playwright/test";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
const CLIENT = process.env.CLIENT ?? "cpc";

/* The route and the page.json of the latest week of the export: the last season, then the last week folder. */
function latestWeek(): { route: string; scene: HeroScene } {
  if (!existsSync(OUT)) throw new Error(`${OUT} does not exist. Run CLIENT=${CLIENT} pnpm build first.`);
  const seasons = readdirSync(OUT).filter((name) => /^\d{4}$/.test(name)).sort();
  for (const season of seasons.reverse()) {
    const weeks = readdirSync(join(OUT, season)).filter((name) => /^week-\d{2}$/.test(name)).sort();
    const week = weeks.at(-1);
    if (week) {
      const page = JSON.parse(readFileSync(join(OUT, season, week, "page.json"), "utf8"));
      return { route: `/${season}/${week}/`, scene: matchupScene(page) };
    }
  }
  throw new Error(`The export of ${CLIENT} holds no week page.`);
}

const { route: WEEK, scene: SCENE } = latestWeek();
const PHONE = { width: 375, height: 812 };
const CANVAS = "canvas[data-hero-scene]";

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

/* Opens the week page in a theme. Each open of the page counts the frames and the canvas contexts that it asks for. */
async function openWeek(page: Page, theme: Theme = "dark"): Promise<void> {
  await page.addInitScript(([key, value]) => localStorage.setItem(key, value), [THEME_KEY, theme] as const);
  await page.addInitScript(() => {
    const counts = { frames: 0, contexts: [] as string[] };
    (window as unknown as { sceneCounts: typeof counts }).sceneCounts = counts;
    const request = window.requestAnimationFrame.bind(window);
    window.requestAnimationFrame = (callback) => {
      counts.frames += 1;
      return request(callback);
    };
    const getContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (this: HTMLCanvasElement, type: string, ...rest: unknown[]) {
      counts.contexts.push(type);
      return (getContext as (...args: unknown[]) => unknown).call(this, type, ...rest);
    } as typeof getContext;
  });
  await page.goto(server.url + WEEK);
  const dark = new RegExp(`(^|\\s)${DARK_CLASS}(\\s|$)`);
  await (theme === "dark" ? expect(page.locator("html")).toHaveClass(dark) : expect(page.locator("html")).not.toHaveClass(dark));
}

const counts = (page: Page) =>
  page.evaluate(() => (window as unknown as { sceneCounts: { frames: number; contexts: string[] } }).sceneCounts);

/* The place of each light in the CSS pixels of the canvas, from the same pure math that the canvas draws with. */
async function lightsOf(page: Page): Promise<ScenePoint[]> {
  const size = await page.locator(CANVAS).evaluate((canvas) => ({ width: canvas.clientWidth, height: canvas.clientHeight }));
  return placeLights(SCENE, { ...size, padding: SCENE_PADDING });
}

/* The page point of a point of the canvas. */
async function onPage(page: Page, point: ScenePoint): Promise<ScenePoint> {
  const box = (await page.locator(CANVAS).boundingBox())!;
  return { x: box.x + point.x, y: box.y + point.y };
}

/* The color of the pixel at a point of the canvas, as #rrggbb. */
async function pixelAt(page: Page, point: ScenePoint): Promise<string> {
  return page.locator(CANVAS).evaluate((canvas: HTMLCanvasElement, at) => {
    const ratio = canvas.width / canvas.clientWidth;
    const [r, g, b] = canvas.getContext("2d")!.getImageData(Math.round(at.x * ratio), Math.round(at.y * ratio), 1, 1).data;
    return `#${[r, g, b].map((value) => value.toString(16).padStart(2, "0")).join("")}`;
  }, point);
}

/* A hex as the long lower-case form, so #fff and #FFFFFF read as one color. */
function longHex(value: string): string {
  return value.trim().toLowerCase().replace(/^#([0-9a-f])([0-9a-f])([0-9a-f])$/, "#$1$1$2$2$3$3");
}

const tokenOf = (page: Page, name: string) =>
  page.evaluate((token) => getComputedStyle(document.documentElement).getPropertyValue(token), name).then(longHex);

const frameOf = (page: Page) => page.locator(CANVAS).evaluate((canvas: HTMLCanvasElement) => canvas.toDataURL());
const stateOf = (page: Page) => page.locator(CANVAS).getAttribute("data-scene-state");
const labelOf = (page: Page) => page.locator(CANVAS).getAttribute("data-scene-label");

const flares = SCENE.lights.flatMap((light, index) => (light.tone === "flare" ? [index] : []));
const restLabel = SCENE.restIndex === null ? "" : SCENE.lights[SCENE.restIndex].label;
const lastIndex = SCENE.lights.length - 1;

/* The Playwright config turns reduced motion on, so the scene draws its settled chart at once in these tests. */
test.describe(`the scene of the week page of ${CLIENT}, at rest`, () => {
  for (const width of [375, 768, 1280]) {
    test(`draws the lights of the chart, with the Matchup in the accent color, at ${width} px (AT-15, AT-34)`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await openWeek(page);
      await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest");
      const lights = await lightsOf(page);
      const accent = await tokenOf(page, "--color-accent");
      const onDark = await tokenOf(page, "--color-on-dark");
      for (const index of flares) expect(await pixelAt(page, lights[index]), SCENE.lights[index].label).toBe(accent);
      const bright = SCENE.lights.findIndex((light) => light.tone === "bright");
      expect(await pixelAt(page, lights[bright])).toBe(onDark);
      await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-label", restLabel);
    });
  }

  test("has exactly one scene, in the first hero of the page, on a 2d context only (AT-35, AT-40)", async ({ page }) => {
    await openWeek(page);
    await expect(page.locator(CANVAS)).toHaveCount(1);
    await expect(page.locator("section").first().locator(CANVAS)).toHaveCount(1);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest");
    expect((await counts(page)).contexts).toEqual(["2d"]);
  });

  test("puts the title above the scene, in a band of at most 140 px, at 375 px (AT-43)", async ({ page }) => {
    await page.setViewportSize(PHONE);
    await openWeek(page);
    const hero = page.locator("section").first();
    const title = (await hero.locator("[data-hero-slot='title']").boundingBox())!;
    const scene = (await hero.locator(CANVAS).boundingBox())!;
    console.log(`${CLIENT}: title top ${title.y}, scene top ${scene.y}, scene height ${scene.height}`);
    expect(title.y + title.height).toBeLessThanOrEqual(scene.y);
    expect(scene.height).toBeLessThanOrEqual(140);
  });

  test("draws the settled chart at once, the same at 0.1 s and 2.5 s, in both themes (AT-31, AT-33)", async ({ page }) => {
    await page.setViewportSize(PHONE);
    await openWeek(page, "light");
    await page.waitForTimeout(100);
    expect(await stateOf(page)).toBe("rest");
    const early = await frameOf(page);
    await page.waitForTimeout(2400);
    expect(await frameOf(page)).toBe(early);
    // The hero stays dark in the light theme, and the canvas draws the same lights in both themes.
    const band = await tokenOf(page, "--color-band");
    expect(await page.locator("section").first().evaluate((hero) => getComputedStyle(hero).backgroundColor)).toBe(
      `rgb(${[1, 3, 5].map((at) => parseInt(band.slice(at, at + 2), 16)).join(", ")})`,
    );
    await openWeek(page, "dark");
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest");
    expect(await frameOf(page)).toBe(early);
  });

  test("selects the nearest light to a tap in empty space, and does not play again (AT-25)", async ({ page }) => {
    await page.setViewportSize(PHONE);
    await openWeek(page);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest");
    const lights = await lightsOf(page);
    // Empty space just right of and under the lowest light, closer to it than to any other light.
    const tap = { x: lights[0].x + 3, y: lights[0].y + 10 };
    expect(nearestLight(lights, tap)).toBe(0);
    const at = await onPage(page, tap);
    await page.mouse.click(at.x, at.y);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-label", SCENE.lights[0].label);
    expect(await stateOf(page)).toBe("rest");
  });

  test("shows the label of the light at the right edge after a tap on it (AT-29)", async ({ page }) => {
    await page.setViewportSize(PHONE);
    await openWeek(page);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest");
    const at = await onPage(page, (await lightsOf(page))[lastIndex]);
    await page.mouse.click(at.x, at.y);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-label", SCENE.lights[lastIndex].label);
  });

  test("moves the selection from light to light with a slide, and stops on the light under the finger (AT-26)", async ({ page }) => {
    await page.setViewportSize(PHONE);
    await openWeek(page);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest");
    const lights = await lightsOf(page);
    const target = SCENE.margin ? SCENE.margin.to : lastIndex;
    const from = await onPage(page, { x: lights[0].x, y: lights[target].y });
    const to = await onPage(page, lights[target]);
    await page.mouse.move(from.x, from.y);
    await page.mouse.down();
    await page.mouse.move(to.x, to.y, { steps: 12 });
    await page.mouse.up();
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-label", SCENE.lights[target].label);
  });

  test("shows the hint until the first tap, and keeps it gone after a reload (AT-28)", async ({ page }) => {
    await page.setViewportSize(PHONE);
    await openWeek(page);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-hint", "shown");
    const at = await onPage(page, (await lightsOf(page))[0]);
    await page.mouse.click(at.x, at.y);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-hint", "gone");
    await page.reload();
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest");
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-hint", "gone");
  });
});

test.describe(`the scene of the week page of ${CLIENT}, with motion`, () => {
  test.use({ reducedMotion: "no-preference" });

  test("settles in about 1.5 s, and is not in the chart at 0.4 s (AT-16)", async ({ page }) => {
    await page.setViewportSize(PHONE);
    // The page records the first time of each state of the canvas, from the first load on.
    await page.addInitScript(() => {
      const times: Record<string, number> = {};
      (window as unknown as { sceneTimes: typeof times }).sceneTimes = times;
      new MutationObserver((changes) => {
        for (const change of changes) {
          const state = (change.target as HTMLElement).dataset.sceneState;
          if (state) times[state] ??= performance.now();
        }
      }).observe(document, { subtree: true, attributeFilter: ["data-scene-state"] });
    });
    await openWeek(page);
    const times = () => page.evaluate(() => (window as unknown as { sceneTimes: Record<string, number> }).sceneTimes);
    await expect.poll(async () => (await times()).settle).toBeGreaterThan(0);
    // At 0.4 s after entry the lights are still on their way, so the frame is not the frame at rest.
    const entry = (await times()).settle;
    await page.waitForFunction((at) => performance.now() >= at + 400, entry);
    expect(await stateOf(page)).toBe("settle");
    const moving = await frameOf(page);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest", { timeout: 5000 });
    expect(await frameOf(page)).not.toBe(moving);
    const settled = (await times()).rest - entry;
    console.log(`${CLIENT}: the scene came to rest ${Math.round(settled)} ms after entry`);
    // The lights settle at 1.5 s and the lines draw by 1.75 s, so the scene is at rest at the check at 1.8 s. A frame can
    // land a little late on a busy machine, so the upper bound has room.
    expect(settled).toBeGreaterThanOrEqual(1750);
    expect(settled).toBeLessThan(2200);
  });

  test("requests no animation frame for 3 s after the settle (AT-32)", async ({ page }) => {
    await page.setViewportSize(PHONE);
    await openWeek(page);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest", { timeout: 5000 });
    // The reveal of each part of the page ends within 1 s of its entry, and the page does not scroll, so no other part moves.
    await page.waitForTimeout(200);
    const before = (await counts(page)).frames;
    await page.waitForTimeout(3000);
    expect((await counts(page)).frames - before).toBe(0);
  });

  test("plays the settle again after the hero leaves the view and comes back (AT-30)", async ({ page }) => {
    await page.setViewportSize(PHONE);
    await openWeek(page);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest", { timeout: 5000 });
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(300);
    await page.evaluate(() => window.scrollTo(0, 0));
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "settle");
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest", { timeout: 5000 });
  });

  test("ignores a tap during the settle, as the selection waits for rest", async ({ page }) => {
    await page.setViewportSize(PHONE);
    await openWeek(page);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "settle");
    const box = (await page.locator(CANVAS).boundingBox())!;
    await page.mouse.click(box.x + 10, box.y + box.height - 10);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest", { timeout: 5000 });
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-label", restLabel);
  });
});

test.describe(`the scene of the week page of ${CLIENT}, on a touch screen`, () => {
  test.use({ hasTouch: true, isMobile: true, viewport: PHONE });

  test("scrolls the page on a vertical swipe that starts in the scene (AT-27)", async ({ page }) => {
    await openWeek(page);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest");
    const box = (await page.locator(CANVAS).boundingBox())!;
    const x = Math.round(box.x + box.width / 2);
    const y = Math.round(box.y + box.height - 20);
    const before = await page.evaluate(() => window.scrollY);
    const session = await page.context().newCDPSession(page);
    await session.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y }] });
    for (let step = 1; step <= 10; step++) {
      await session.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x, y: y - step * 30 }] });
    }
    await session.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    await expect.poll(() => page.evaluate(() => window.scrollY)).toBeGreaterThan(before + 100);
  });
});
