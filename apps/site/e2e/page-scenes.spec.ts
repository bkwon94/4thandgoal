/**
 * The heroes of the rankings page, the midseason report, the home page, the analyzer, and the 404 page, on the static
 * export in out/ of the current CLIENT, in Chromium. It checks the static heroes, the count of scenes, and the drift.
 */
import { DARK_CLASS, THEME_KEY } from "@cpc/design/lib/theme";
import { midseasonSchema } from "@cpc/midseason/schema/midseason";
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

/* The midseason report. A client with no report has no report page. */
const MIDSEASON = published("midseason.json", (json) => midseasonSchema.parse(json));

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

/* Checks that a hero is static: the texture layer of the grid and the glow, the four brackets, and no scene canvas.
   It finds the hero by its label in the markup, not by its role, because the passphrase dialog of the analyzer hides
   the page under it from the tree of roles. */
async function expectStatic(page: Page, name: string): Promise<void> {
  const hero = page.locator(`section[aria-label="${name}"]`);
  await expect(hero).toHaveCount(1);
  await expect(hero.locator("[data-hero-art='texture']")).toHaveCount(1);
  await expect(hero.locator("[data-hero-art='bracket']")).toHaveCount(4);
  await expect(hero.locator(CANVAS)).toHaveCount(0);
  console.log(`${CLIENT}: the hero "${name}" is static, with ${await page.locator(CANVAS).count()} scene canvases on the page`);
}

/* The rankings, the midseason report, the home takeover, and the analyzer keep the static grid. Only the week page, the
   home Matchup hero, the manager pages, and the 404 draw a scene. */
test.describe(`the static heroes of ${CLIENT}`, () => {
  test.use({ viewport: PHONE });

  test("the rankings page has no scene, and its hero is static (AT-35, AT-44)", async ({ page }) => {
    await open(page, "/rankings/");
    await expectStatic(page, "Rank 1");
    await expect(page.locator(CANVAS)).toHaveCount(0);
  });

  test("the report has no scene, and its opener is static (AT-35, AT-44)", async ({ page }) => {
    test.skip(!MIDSEASON, `${CLIENT} has no midseason report`);
    await open(page, `/midseason/${SEASON}/`);
    await expectStatic(page, MIDSEASON!.opener.title);
    await expect(page.locator(CANVAS)).toHaveCount(0);
  });

  test("the home page has no scene under the takeover, and one in the Matchup hero without it (AT-35, AT-44)", async ({ page }) => {
    await open(page, "/");
    const takeover = page.getByRole("region", { name: `${SEASON} Midseason Report`, exact: true });
    if ((await takeover.count()) > 0) {
      await expectStatic(page, `${SEASON} Midseason Report`);
      await expect(page.locator(CANVAS)).toHaveCount(0);
    } else {
      await expect(page.locator(CANVAS)).toHaveCount(1);
      await expect(page.getByRole("region", { name: "Matchup of the Week" }).locator(CANVAS)).toHaveCount(1);
      await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest");
    }
  });

  test("the analyzer has no scene before a grade, and its title hero is static (AT-35, AT-44)", async ({ page }) => {
    await open(page, "/analyze/");
    await expectStatic(page, "Trade Analyzer");
    await expect(page.locator(CANVAS)).toHaveCount(0);
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
