/**
 * The hero scene of a manager page on the static export in out/ of the current CLIENT, in Chromium.
 * It checks one light per played week, bright for a win and dim for a loss, the dashed median, the label, and the grade popover.
 */
import { DARK_CLASS, THEME_KEY } from "@cpc/design/lib/theme";
import { type HeroScene, SCENE_PADDING, type ScenePoint, placeGuides, placeLights } from "@cpc/design/parts/scene-math";
import { managerScene } from "@cpc/managers/page/manager-scene";
import type { ManagersFile } from "@cpc/managers/schema/manager-types";
import { expect, test, type Page } from "@playwright/test";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
const CLIENT = process.env.CLIENT ?? "cpc";
const CANVAS = "canvas[data-hero-scene]";

/* Roster 7 is the manager of AT-18 in cpc. A client with no roster 7 takes its first manager. */
const ROSTER = 7;

/* The route and the scene of the manager page, from the managers file of the latest season of the export. */
function managerPage(): { route: string; scene: HeroScene; rosterId: number } | null {
  if (!existsSync(OUT)) throw new Error(`${OUT} does not exist. Run CLIENT=${CLIENT} pnpm build first.`);
  const seasons = readdirSync(OUT).filter((name) => /^\d{4}$/.test(name)).sort();
  for (const season of seasons.reverse()) {
    const path = join(OUT, season, "managers.json");
    if (!existsSync(path)) continue;
    const { managers } = JSON.parse(readFileSync(path, "utf8")) as ManagersFile;
    const manager = managers.find((entry) => entry.roster_id === ROSTER) ?? managers[0];
    if (manager) return { route: `/${season}/managers/${manager.roster_id}/`, scene: managerScene(manager), rosterId: manager.roster_id };
  }
  return null;
}

const found = managerPage();

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

/* Opens the manager page in the dark theme and waits for the scene at rest. Reduced motion draws the rest at once. */
async function openManager(page: Page, width: number): Promise<void> {
  await page.setViewportSize({ width, height: 900 });
  await page.addInitScript(([key, value]) => localStorage.setItem(key, value), [THEME_KEY, "dark"] as const);
  await page.goto(server.url + found!.route);
  await expect(page.locator("html")).toHaveClass(new RegExp(`(^|\\s)${DARK_CLASS}(\\s|$)`));
  await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-state", "rest");
}

/* The size of the canvas in CSS pixels, as the box of the pure math. */
async function boxOf(page: Page) {
  const size = await page.locator(CANVAS).evaluate((canvas) => ({ width: canvas.clientWidth, height: canvas.clientHeight }));
  return { ...size, padding: SCENE_PADDING };
}

/* The color and the alpha of the pixel at each point of the canvas, as [r, g, b, a]. */
function pixelsAt(page: Page, points: ScenePoint[]): Promise<number[][]> {
  return page.locator(CANVAS).evaluate((canvas: HTMLCanvasElement, at) => {
    const ratio = canvas.width / canvas.clientWidth;
    const ctx = canvas.getContext("2d")!;
    return at.map((point) => [...ctx.getImageData(Math.round(point.x * ratio), Math.round(point.y * ratio), 1, 1).data]);
  }, points);
}

/* The on-dark color of the page as [r, g, b]. */
async function onDarkOf(page: Page): Promise<number[]> {
  const hex = (await page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue("--color-on-dark"))).trim();
  const long = hex.replace(/^#([0-9a-f])([0-9a-f])([0-9a-f])$/i, "#$1$1$2$2$3$3");
  return [1, 3, 5].map((at) => parseInt(long.slice(at, at + 2), 16));
}

test.describe(`the scene of a manager page of ${CLIENT}`, () => {
  test.skip(found === null, `The export of ${CLIENT} holds no managers file.`);

  for (const width of [375, 768, 1280]) {
    test(`draws one light per played week, bright for a win and dim for a loss, with the dashed median, at ${width} px (AT-18)`, async ({ page }) => {
      const { scene } = found!;
      await openManager(page, width);
      await expect(page.locator(CANVAS)).toHaveCount(1);
      await expect(page.locator("section").first().locator(CANVAS)).toHaveCount(1);
      const box = await boxOf(page);
      const lights = placeLights(scene, box);
      const pixels = await pixelsAt(page, lights);
      const onDark = await onDarkOf(page);
      scene.lights.forEach((light, index) => {
        const [r, g, b, a] = pixels[index];
        // A bright light is the full on-dark color. A dim light draws at part opacity, so the canvas stays part clear.
        if (light.tone === "bright") expect([r, g, b, a], light.label).toEqual([...onDark, 255]);
        else expect(a, light.label).toBeLessThan(255);
      });

      // The median of each week: the samples along the line, away from each light, hit both the dashes and the gaps.
      const [guide] = placeGuides(scene, box);
      const samples: ScenePoint[] = [];
      for (let step = 0; step < guide.points.length - 1; step++) {
        const [a, b] = [guide.points[step], guide.points[step + 1]];
        for (let share = 0; share < 1; share += 0.02) samples.push({ x: a.x + (b.x - a.x) * share, y: a.y + (b.y - a.y) * share });
      }
      const clear = samples.filter((point) => lights.every((light) => Math.hypot(light.x - point.x, light.y - point.y) > 10));
      const alphas = (await pixelsAt(page, clear)).map(([, , , a]) => a);
      expect(alphas.filter((a) => a > 0).length).toBeGreaterThan(clear.length / 5);
      expect(alphas.filter((a) => a === 0).length).toBeGreaterThan(clear.length / 5);

      await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-label", scene.lights.at(-1)!.label);
    });
  }

  test("draws the weeks of roster 7 in cpc: weeks 3, 4, and 8 bright, and week 8 labeled at rest (AT-18)", async ({ page }) => {
    test.skip(CLIENT !== "cpc" || found!.rosterId !== ROSTER, "The weeks of AT-18 are the weeks of roster 7 in cpc.");
    const { scene } = found!;
    expect(scene.lights.map((light) => light.x)).toEqual([1, 2, 3, 4, 5, 6, 7, 8]);
    expect(scene.lights.flatMap((light) => (light.tone === "bright" ? [light.x] : []))).toEqual([3, 4, 8]);
    expect(scene.guides).toHaveLength(1);
    await openManager(page, 375);
    await expect(page.locator(CANVAS)).toHaveAttribute("data-scene-label", "Week 8 · 118.89 · W");
  });

  for (const width of [375, 1280]) {
    test(`opens the grade popover on a tap of the grade letter over the scene, at ${width} px (AT-36)`, async ({ page }) => {
      await openManager(page, width);
      const trigger = page.getByRole("button", { name: /^Grade [A-F][+-]?, how the grade reads$/ });
      test.skip((await trigger.count()) === 0, "This manager has no grade.");
      await trigger.click();
      await expect(page.getByRole("dialog", { name: "How The Grade Reads" })).toBeVisible();
    });
  }
});
