/**
 * The stage of the analyzer hero on the static export of the current CLIENT. Idle: the mesh holds still, pauses out of
 * view and in a hidden tab, and each hero text over it reaches 4.5:1. Wait: the mesh weighs each side in turn.
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
const WAIT_HERO = 'section[aria-label="Grading the Trade"]';
const WAIT_CANVAS = `${WAIT_HERO} canvas[data-hero-mesh]`;
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
    const path = new URL(request.url()).pathname;
    // The grade and the search are held: the route answers the preflight and never answers the POST, so the wait
    // runs for as long as the test samples it. The page closes with the request still open.
    const held = path.endsWith("/analyze") || path.endsWith("/find");
    if (held && request.method() === "OPTIONS") return route.fulfill({ status: 204, headers: CORS });
    if (held) return;
    if (!path.endsWith("/teams")) return route.abort();
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

/* The query of the trade on the stage, so the Stack opens with the trade in it. */
function stageQuery(): string {
  const trade = stageTrade(TEAMS);
  return `?team=${trade.team}&with=${trade.with}&give=${trade.give.join(",")}&get=${trade.get.join(",")}`;
}

/*
 * Taps "Grade the Trade" in the page and gives the time in ms from the tap until the wait shows: the stage line
 * "Weighing the sides" is on the screen, and two frames of the wait mesh differ.
 */
async function tapAndTimeWait(page: Page): Promise<number> {
  const button = page.getByRole("button", { name: "Grade the Trade" });
  await expect(button).toBeEnabled();
  const handle = await button.elementHandle();
  return page.evaluate(
    ([el, hero]) =>
      new Promise<number>((done, fail) => {
        let last: number | null = null;
        const start = performance.now();
        (el as HTMLElement).click();
        const check = () => {
          const elapsed = performance.now() - start;
          if (elapsed > 2000) return fail(new Error("the wait did not show within 2 s"));
          const line = document.querySelector(`${hero} .t-think-text:last-child`);
          const canvas = document.querySelector<HTMLCanvasElement>(`${hero} canvas[data-hero-mesh]`);
          const ctx = canvas && canvas.width > 1 ? canvas.getContext("2d") : null;
          if (line?.textContent === "Weighing the sides" && ctx) {
            // A cheap sum of the canvas: two frames of a moving mesh never sum the same.
            const data = ctx.getImageData(0, 0, canvas!.width, canvas!.height).data;
            let sum = 0;
            for (let k = 0; k < data.length; k += 4) sum += data[k] * 3 + data[k + 1] * 5 + data[k + 3] * 7;
            if (last !== null && sum !== last) return done(elapsed);
            last = sum;
          }
          requestAnimationFrame(check);
        };
        requestAnimationFrame(check);
      }),
    [handle, WAIT_HERO] as const,
  );
}

/* Waits until no stage line is mid-swap. A line that fades in for 150 ms has a mixed color for that moment only, as a
   part that fades in on the load does in `openPage`, so the scan reads the line at rest. The mesh keeps moving. */
const lineAtRest = (page: Page) =>
  page.evaluate(() =>
    Promise.all(
      document
        .getAnimations()
        .filter((animation) => animation.effect?.getComputedTiming().endTime !== Infinity)
        .map((animation) => animation.finished.catch(() => undefined)),
    ),
  );

/* The pull of each weight under the mesh now, in the order of the sides, which the canvas keeps for the evidence. */
const pulls = (page: Page) =>
  page.locator(WAIT_CANVAS).evaluate((el) => ((el as HTMLCanvasElement).dataset.meshPulls ?? "").split(",").filter(Boolean).map(Number));

test.describe("the wait, with motion on", () => {
  test.use({ reducedMotion: "no-preference" });

  for (const width of [375, 768, 1280]) {
    test(`wait start: ${CLIENT} the mesh moves and "Weighing the sides" shows within 100 ms of the tap, ${width}px (AT-3)`, async ({ page }, info) => {
      await page.setViewportSize({ width, height: 900 });
      await openAnalyzer(page, stageQuery());
      await settle(page);
      const elapsed = await tapAndTimeWait(page);
      console.log(`wait start: ${CLIENT} ${width}px: ${elapsed.toFixed(1)} ms from the tap`);
      await page.locator(WAIT_HERO).screenshot({ path: info.outputPath(`wait-start-${CLIENT}-${width}.png`) });
      expect(elapsed).toBeLessThanOrEqual(100);
    });
  }

  test(`wait dips: ${CLIENT} the mesh dips under each side in turn, about 1.25 s each, 1280px (AT-5)`, async ({ browser }, info) => {
    // A page of its own records a video of the wait, which is the recording of AT-5.
    const context = await browser.newContext({
      viewport: { width: 1280, height: 900 },
      reducedMotion: "no-preference",
      recordVideo: { dir: info.outputPath("video"), size: { width: 1280, height: 900 } },
    });
    const page = await context.newPage();
    await openAnalyzer(page, stageQuery());
    await settle(page);
    await tapAndTimeWait(page);
    // The side that pulls hardest at each sample, or -1 when no weight pulls, with the time of the sample.
    const samples: { at: number; side: number }[] = [];
    const start = Date.now();
    let shot = 0;
    while (Date.now() - start < 5000) {
      const now = await pulls(page);
      const top = Math.max(...now);
      const side = top > 0.05 ? now.indexOf(top) : -1;
      if (side >= 0 && samples.at(-1)?.side !== side && shot < 4) {
        await page.waitForTimeout(500);
        await page.locator(WAIT_HERO).screenshot({ path: info.outputPath(`wait-dip-${CLIENT}-${shot++}-side-${side}.png`) });
      }
      samples.push({ at: Date.now() - start, side });
      await page.waitForTimeout(40);
    }
    // The runs of one side, with the time each starts and ends.
    const runs: { side: number; from: number; to: number }[] = [];
    for (const { at, side } of samples) {
      if (side < 0) continue;
      const run = runs.at(-1);
      if (run && run.side === side) run.to = at;
      else runs.push({ side, from: at, to: at });
    }
    console.log(`wait dips: ${CLIENT}: ${runs.map((r) => `side ${r.side} ${r.from}-${r.to} ms`).join(", ")}`);
    await context.close();
    console.log(`wait dips: ${CLIENT}: the recording is ${await page.video()?.path()}`);
    expect(runs.map((r) => r.side).slice(0, 4)).toEqual([0, 1, 0, 1]);
    // Each full turn in the middle of the sample holds about 1.25 s. The turn starts and ends at a small pull, so the
    // part above the cut is a little shorter than the turn, and the gaps of the samples take some more.
    for (const run of runs.slice(1, -1)) {
      const turn = runs[runs.indexOf(run) + 1].from - run.from;
      expect(turn, `side ${run.side} held the weight ${turn} ms`).toBeGreaterThan(1000);
      expect(turn, `side ${run.side} held the weight ${turn} ms`).toBeLessThan(1500);
    }
  });

  test(`wait frames: ${CLIENT} no frame of the wait takes longer than 50 ms after the first second, 375px, 4x CPU slowdown (AT-15)`, async ({ page }, info) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await openAnalyzer(page, stageQuery());
    await settle(page);
    const cdp = await page.context().newCDPSession(page);
    await cdp.send("Emulation.setCPUThrottlingRate", { rate: 4 });
    try {
      await page.evaluate(() => {
        const w = window as unknown as { frameTimes: number[] };
        w.frameTimes = [];
        const tick = (now: number) => {
          w.frameTimes.push(now);
          requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      });
      await tapAndTimeWait(page);
      const tapped = await page.evaluate(() => performance.now());
      await page.waitForTimeout(5000);
      const deltas = await page.evaluate((from) => {
        const times = (window as unknown as { frameTimes: number[] }).frameTimes.filter((t) => t >= from);
        return times.slice(1).map((t, i) => t - times[i]);
      }, tapped + 1000);
      await page.locator(WAIT_HERO).screenshot({ path: info.outputPath(`wait-frames-${CLIENT}-375.png`) });
      const longest = Math.max(...deltas);
      console.log(`wait frames: ${CLIENT} 375px 4x: ${deltas.length} frames, longest ${longest.toFixed(1)} ms`);
      expect(deltas.length).toBeGreaterThan(30);
      expect(longest).toBeLessThanOrEqual(50);
    } finally {
      await cdp.send("Emulation.setCPUThrottlingRate", { rate: 1 });
    }
  });

  /* The mesh moves in the wait, so the scan reads it at least 10 times over 3 s and keeps each failure it finds. */
  for (const theme of ["dark", "light"] as const) {
    for (const width of [390, 1280]) {
      test(`wait contrast: ${CLIENT} each hero text reaches 4.5:1 in 10 samples over 3 s of the wait, ${theme} ${width}px (AT-20)`, async ({ page }, info) => {
        await page.setViewportSize({ width, height: 900 });
        await openAnalyzer(page, stageQuery(), theme);
        await settle(page);
        await tapAndTimeWait(page);
        const start = Date.now();
        const failures: string[] = [];
        let samples = 0;
        while (samples < 10 || Date.now() - start < 3000) {
          await lineAtRest(page);
          failures.push(...(await scanHeroPixels(page, WAIT_HERO)));
          samples++;
          await page.waitForTimeout(150);
        }
        await page.locator(WAIT_HERO).screenshot({ path: info.outputPath(`wait-contrast-${CLIENT}-${theme}-${width}.png`) });
        console.log(`wait contrast: ${CLIENT} ${theme} ${width}px: ${samples} samples over ${Date.now() - start} ms`);
        expect([...new Set(failures)], `the wait hero of ${CLIENT} breaks the readability floor`).toEqual([]);
      });
    }
  }

  test(`finder wait: ${CLIENT} the Finder wait shows the Sweep bar, and the hero shows no wait mesh and no stage line (AT-23)`, async ({ page }, info) => {
    test.skip(CLIENT !== "norcal", "the Finder is on in norcal only");
    await page.setViewportSize({ width: 1280, height: 900 });
    const trade = stageTrade(TEAMS);
    await openAnalyzer(page, `?team=${trade.team}`);
    await page.getByRole("button", { name: "Find a Trade" }).click();
    const finder = page.locator('section[aria-labelledby="find-trade"]');
    await expect(finder.getByRole("button", { name: "Finding…" })).toBeVisible();
    await expect(finder.locator('[role="presentation"]')).toBeVisible();
    await finder.screenshot({ path: info.outputPath(`finder-wait-${CLIENT}-1280.png`) });
    expect(await finder.locator("canvas").count()).toBe(0);
    expect(await page.locator(WAIT_HERO).count()).toBe(0);
    expect(await page.locator(".t-think").count()).toBe(0);
  });
});

test.describe("the wait, with motion off", () => {
  test(`wait still: ${CLIENT} the mesh of the wait stays still and flat, 1280px`, async ({ page }, info) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    await openAnalyzer(page, stageQuery());
    await page.getByRole("button", { name: "Grade the Trade" }).click();
    const canvas = page.locator(WAIT_CANVAS);
    await expect(canvas).toBeVisible();
    await page.waitForTimeout(500);
    const first = await canvas.screenshot({ path: info.outputPath(`wait-still-${CLIENT}-a.png`) });
    await page.waitForTimeout(1500);
    const second = await canvas.screenshot({ path: info.outputPath(`wait-still-${CLIENT}-b.png`) });
    expect(first.equals(second), "the mesh moved in the wait with motion off").toBe(true);
    expect((await pulls(page)).every((p) => p === 0)).toBe(true);
  });
});
