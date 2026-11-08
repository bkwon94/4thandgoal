/**
 * The hero scenes of the rankings page, the midseason report, the home page, and the 404 page, on the static export in
 * out/ of the current CLIENT, in Chromium. It checks the flare, the label at rest, the count of scenes, and the drift.
 */
import { DARK_CLASS, THEME_KEY } from "@cpc/design/lib/theme";
import { type HeroScene, SCENE_PADDING, placeLights } from "@cpc/design/parts/scene-math";
import { midseasonScene } from "@cpc/midseason/report/midseason-scene";
import { midseasonSchema } from "@cpc/midseason/schema/midseason";
import { rankingsScene } from "@cpc/rankings/chapters/rankings-scene";
import { rankingsSchema } from "@cpc/rankings/schema/rankings";
import { expect, test, type Page } from "@playwright/test";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
const CLIENT = process.env.CLIENT ?? "cpc";
const CANVAS = "canvas[data-hero-scene]";
const PHONE = { width: 375, height: 812 };

/* The last season folder of the export, the season of the latest week. */
function latestSeason(): string {
  if (!existsSync(OUT)) throw new Error(`${OUT} does not exist. Run CLIENT=${CLIENT} pnpm build first.`);
  const season = readdirSync(OUT).filter((name) => /^\d{4}$/.test(name)).sort().at(-1);
  if (!season) throw new Error(`The export of ${CLIENT} holds no season.`);
  return season;
}

const SEASON = latestSeason();

/* A published file of the season, parsed by its schema, or null when the client has not published it. */
function published<T>(name: string, parse: (json: unknown) => T): T | null {
  const path = join(OUT, SEASON, name);
  return existsSync(path) ? parse(JSON.parse(readFileSync(path, "utf8"))) : null;
}

/* The scene of the latest week of the rankings file, as the rankings page opens on that week. */
const RANKINGS = published("rankings.json", (json) => rankingsSchema.parse(json));
const RANKINGS_SCENE = RANKINGS ? rankingsScene(RANKINGS.weeks.at(-1)!) : undefined;

/* The midseason report and its scene. A client with no report has no report page. */
const MIDSEASON = published("midseason.json", (json) => midseasonSchema.parse(json));
const MIDSEASON_SCENE = MIDSEASON ? midseasonScene(MIDSEASON) : undefined;

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

/* Opens a route in the dark theme. Every state of the canvas from the first load on goes into a list of the page. */
async function open(page: Page, route: string): Promise<void> {
  await page.addInitScript(([key]) => localStorage.setItem(key, "dark"), [THEME_KEY] as const);
  await page.addInitScript(() => {
    const states: { state: string; at: number }[] = [];
    (window as unknown as { sceneStates: typeof states }).sceneStates = states;
    new MutationObserver((changes) => {
      for (const change of changes) {
        const state = (change.target as HTMLElement).dataset.sceneState;
        if (state && states.at(-1)?.state !== state) states.push({ state, at: performance.now() });
      }
    }).observe(document, { subtree: true, attributeFilter: ["data-scene-state"] });
  });
  await page.goto(server.url + route);
  await expect(page.locator("html")).toHaveClass(new RegExp(`(^|\\s)${DARK_CLASS}(\\s|$)`));
}

const statesOf = (page: Page) =>
  page.evaluate(() => (window as unknown as { sceneStates: { state: string; at: number }[] }).sceneStates);

const frameOf = (page: Page) => page.locator(CANVAS).evaluate((canvas: HTMLCanvasElement) => canvas.toDataURL());

/* The accent token as the long lower-case hex, as the canvas pixel reads. */
const accentOf = (page: Page) =>
  page
    .evaluate(() => getComputedStyle(document.documentElement).getPropertyValue("--color-accent"))
    .then((value) => value.trim().toLowerCase().replace(/^#([0-9a-f])([0-9a-f])([0-9a-f])$/, "#$1$1$2$2$3$3"));

/* The color of the pixel at the light of an index, from the same pure math that the canvas draws with. */
async function lightPixel(page: Page, scene: HeroScene, index: number): Promise<string> {
  const size = await page.locator(CANVAS).evaluate((canvas) => ({ width: canvas.clientWidth, height: canvas.clientHeight }));
  const at = placeLights(scene, { ...size, padding: SCENE_PADDING })[index];
  return page.locator(CANVAS).evaluate((canvas: HTMLCanvasElement, point) => {
    const ratio = canvas.width / canvas.clientWidth;
    const [r, g, b] = canvas.getContext("2d")!.getImageData(Math.round(point.x * ratio), Math.round(point.y * ratio), 1, 1).data;
    return `#${[r, g, b].map((value) => value.toString(16).padStart(2, "0")).join("")}`;
  }, at);
}

/* The Playwright config turns reduced motion on, so a settle scene draws its chart at once in these tests. */
test.describe(`the scenes of the pages of ${CLIENT}, at rest`, () => {
  for (const width of [375, 768, 1280]) {
    test(`the rankings scene flares rank 1 and shows its label at ${width} px (AT-19)`, async ({ page }) => {
      test.skip(!RANKINGS_SCENE, `${CLIENT} has no rankings week with odds`);
      const scene = RANKINGS_SCENE!;
      await page.setViewportSize({ width, height: 900 });
      await open(page, "/rankings/");
      await expect(page.locator(CANVAS)).toHaveCount(1);
      await expect(page.getByRole("region", { name: "Rank 1" }).locator(CANVAS)).toHaveCount(1);
      await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest");
      await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-label", scene.lights[0].label);
      expect(await lightPixel(page, scene, 0)).toBe(await accentOf(page));
      console.log(`${CLIENT}: the rank-1 light reads "${scene.lights[0].label}"`);
    });

    test(`the midseason scene flares the leader and shows its label at ${width} px (AT-22)`, async ({ page }) => {
      test.skip(!MIDSEASON_SCENE, `${CLIENT} has no midseason report`);
      const scene = MIDSEASON_SCENE!;
      await page.setViewportSize({ width, height: 900 });
      await open(page, `/midseason/${SEASON}/`);
      await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest");
      await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-label", scene.lights[0].label);
      expect(await lightPixel(page, scene, 0)).toBe(await accentOf(page));
      console.log(`${CLIENT}: the leader light reads "${scene.lights[0].label}"`);
    });
  }

  test("the report has one scene, in the opener, and none in an act title (AT-35)", async ({ page }) => {
    test.skip(!MIDSEASON, `${CLIENT} has no midseason report`);
    await page.setViewportSize(PHONE);
    await open(page, `/midseason/${SEASON}/`);
    await expect(page.locator(CANVAS)).toHaveCount(1);
    await expect(page.getByRole("region", { name: MIDSEASON!.opener.title, exact: true }).locator(CANVAS)).toHaveCount(1);
    for (const [index, act] of MIDSEASON!.acts.entries()) {
      const title = page.getByRole("region", { name: `Act ${["I", "II", "III"][index]}: ${act.title}`, exact: true });
      await expect(title).toHaveCount(1);
      await expect(title.locator(CANVAS)).toHaveCount(0);
    }
  });

  test("the home page has exactly one scene, in its first hero (AT-35)", async ({ page }) => {
    await page.setViewportSize(PHONE);
    await open(page, "/");
    await expect(page.locator(CANVAS)).toHaveCount(1);
    await expect(page.locator("section[aria-label]").filter({ has: page.locator(CANVAS) })).toHaveCount(1);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest");
  });
});

test.describe(`the 404 scene of ${CLIENT}, with motion`, () => {
  test.use({ reducedMotion: "no-preference", viewport: PHONE });

  test("drifts, so the frames at 2 s and 6 s differ, and never settles (AT-23)", async ({ page }) => {
    await open(page, "/no-such-page/");
    await expect(page.getByRole("region", { name: "Page not found" }).locator(CANVAS)).toHaveCount(1);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "drift");
    const entry = (await statesOf(page)).find((change) => change.state === "drift")!.at;
    const at = (ms: number) => page.waitForFunction((time) => performance.now() >= time, entry + ms);
    await at(2000);
    const early = await frameOf(page);
    await at(6000);
    const late = await frameOf(page);
    expect(late).not.toBe(early);
    // The scene waits in idle until the hero enters the view, then never leaves the drift: no settle, no rest, no label.
    expect((await statesOf(page)).map((change) => change.state).filter((state) => state !== "idle")).toEqual(["drift"]);
    expect(await page.locator(CANVAS).getAttribute("data-scene-state")).toBe("drift");
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-label", "");
  });
});
