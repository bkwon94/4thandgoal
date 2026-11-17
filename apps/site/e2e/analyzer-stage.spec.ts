/**
 * The idle stage of the analyzer hero on the static export of the current CLIENT: the mesh holds still, pauses out of
 * view and in a hidden tab, and each hero text over it reaches 4.5:1 with the players of a real trade on the stage.
 */
import type { Theme } from "@cpc/design/lib/theme";
import { expect, test, type Page } from "@playwright/test";
import { join } from "node:path";
import { rawTeams, type RawTeam } from "../src/fixtures/raw-teams";
import { openPage, scanHeroPixels } from "./floor";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
const CLIENT = process.env.CLIENT ?? "cpc";
const HERO = 'section[aria-label="Trade Analyzer"]';
const CANVAS = `${HERO} canvas[data-hero-mesh]`;
const CORS = { "access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "GET, POST" };

/* The teams of the latest weekly build of the client, as the teams route of the API gives them. */
const TEAMS = rawTeams(CLIENT);

/* The trade on the stage. In cpc it is trade T of the spec: Bo Girds gives Kenneth Walker III to Teehee for Tee Higgins
   and Bhayshul Tuten. Another client takes its two longest team names, so a long column label must fit, with one player
   given and two got. */
function stageTrade(teams: RawTeam[]): { team: number; with: number; give: string[]; get: string[] } {
  if (CLIENT === "cpc") return { team: 6, with: 12, give: ["8151"], get: ["6801", "12490"] };
  const [mine, theirs] = [...teams].filter((t) => t.players.length >= 2).sort((a, b) => b.team.length - a.team.length || a.roster_id - b.roster_id);
  return { team: mine.roster_id, with: theirs.roster_id, give: [mine.players[0].player_id], get: theirs.players.slice(0, 2).map((p) => p.player_id) };
}

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

/* The analyzer with a stored passphrase, so no dialog covers the page. The teams route answers with the real rosters,
   and every other call off this machine fails, so no test reaches the live API. */
async function openAnalyzer(page: Page, query = "", theme: Theme = "dark") {
  await page.route((url) => !["127.0.0.1", "localhost"].includes(url.hostname), (route) => {
    const request = route.request();
    if (!new URL(request.url()).pathname.endsWith("/teams")) return route.abort();
    if (request.method() === "OPTIONS") return route.fulfill({ status: 204, headers: CORS });
    return route.fulfill({ status: 200, headers: CORS, contentType: "application/json", body: JSON.stringify({ teams: TEAMS }) });
  });
  await page.addInitScript(() => localStorage.setItem("cpc.passphrase", "test"));
  await openPage(page, `${server.url}/analyze/${query}`, theme);
  await expect.poll(() => frames(page)).toBeGreaterThan(0);
}

/* The count of the frames the mesh drew, which the canvas keeps for this check. */
const frames = (page: Page) => page.locator(CANVAS).evaluate((el) => Number((el as HTMLCanvasElement).dataset.meshFrames ?? 0));

/* Waits until the mesh draws no frame for half a second, so a shot or a count starts from a mesh at rest. */
async function settle(page: Page) {
  let before = -1;
  for (let now = await frames(page); now !== before; now = await frames(page)) {
    before = now;
    await page.waitForTimeout(500);
  }
}

test.describe("with motion on", () => {
  test.use({ reducedMotion: "no-preference" });

  test(`idle mesh: ${CLIENT} shows the same flat mesh in two shots 2 s apart, empty Stack, 1280px (AT-1)`, async ({ page }, info) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await openAnalyzer(page);
    await page.waitForTimeout(3000);
    const first = await page.locator(HERO).screenshot({ path: info.outputPath(`idle-${CLIENT}-1280-a.png`) });
    await page.waitForTimeout(2000);
    const second = await page.locator(HERO).screenshot({ path: info.outputPath(`idle-${CLIENT}-1280-b.png`) });
    expect(first.equals(second), "the idle mesh moved between the two shots").toBe(true);
  });

  test(`idle mesh: ${CLIENT} draws no frame out of view or in a hidden tab, 390px (AT-16)`, async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 360 });
    await openAnalyzer(page);
    await settle(page);

    // Out of view: a resize clears the canvas and owes a frame, and the frame waits until the hero is back in view.
    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
    await expect(page.locator(HERO)).not.toBeInViewport();
    const away = await frames(page);
    await page.setViewportSize({ width: 420, height: 360 });
    await page.waitForTimeout(2000);
    expect(await frames(page), "the mesh drew a frame out of view").toBe(away);
    await page.evaluate(() => window.scrollTo(0, 0));
    await expect.poll(() => frames(page)).toBeGreaterThan(away);
    await settle(page);

    // A hidden tab: the browser of the test never hides its one tab, so the page reports hidden as a background tab does.
    const shown = await frames(page);
    await page.evaluate(() => {
      Object.defineProperty(document, "hidden", { configurable: true, get: () => true });
      Object.defineProperty(document, "visibilityState", { configurable: true, get: () => "hidden" });
      document.dispatchEvent(new Event("visibilitychange"));
    });
    await page.setViewportSize({ width: 390, height: 360 });
    await page.waitForTimeout(2000);
    expect(await frames(page), "the mesh drew a frame in a hidden tab").toBe(shown);
    await page.evaluate(() => {
      Object.defineProperty(document, "hidden", { configurable: true, get: () => false });
      Object.defineProperty(document, "visibilityState", { configurable: true, get: () => "visible" });
      document.dispatchEvent(new Event("visibilitychange"));
    });
    await expect.poll(() => frames(page)).toBeGreaterThan(shown);
  });
});

/* The floor runs with motion off. The idle mesh is the same still mesh either way, so the pixel scan reads idle here. */
for (const theme of ["dark", "light"] as const) {
  for (const width of [390, 1280]) {
    test(`idle contrast: ${CLIENT} each hero text over the mesh reaches 4.5:1 with a trade on the stage, ${theme} ${width}px (AT-20)`, async ({ page }, info) => {
      const trade = stageTrade(TEAMS);
      const names = trade.get.map((id) => TEAMS.find((t) => t.roster_id === trade.with)!.players.find((p) => p.player_id === id)!.name);
      await page.setViewportSize({ width, height: 900 });
      await openAnalyzer(page, `?team=${trade.team}&with=${trade.with}&give=${trade.give.join(",")}&get=${trade.get.join(",")}`, theme);
      const hero = page.locator(HERO);
      for (const name of names) await expect(hero.getByText(name, { exact: true })).toBeVisible();
      await settle(page);
      await hero.screenshot({ path: info.outputPath(`idle-stage-${CLIENT}-${theme}-${width}.png`) });
      expect(await scanHeroPixels(page, HERO), `the idle hero of ${CLIENT} breaks the readability floor`).toEqual([]);
    });
  }
}

/* A side with no player yet shows a placeholder in place of a chip. Its small muted text sits on the mesh with no chip
   under it, so it gets its own pixel scan. */
for (const width of [390, 1280]) {
  test(`idle contrast: ${CLIENT} the placeholder of a side with no player reaches 4.5:1, dark ${width}px (AT-20)`, async ({ page }, info) => {
    const trade = stageTrade(TEAMS);
    await page.setViewportSize({ width, height: 900 });
    await openAnalyzer(page, `?team=${trade.team}&with=${trade.with}&give=${trade.give.join(",")}`);
    const hero = page.locator(HERO);
    await expect(hero.getByText("No player yet")).toBeVisible();
    await settle(page);
    await hero.screenshot({ path: info.outputPath(`idle-stage-one-side-${CLIENT}-${width}.png`) });
    expect(await scanHeroPixels(page, HERO), `the idle hero of ${CLIENT} breaks the readability floor`).toEqual([]);
  });
}
