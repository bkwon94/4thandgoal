/**
 * The stage of the analyzer hero on the static export of the current CLIENT.
 * The tests cover the idle stage, the wait, the reveal, and the result, with motion on and with motion off.
 */
import type { Theme } from "@cpc/design/lib/theme";
import { favoredSide } from "@cpc/analyzer/lib/favored-side";
import type { AnalyzeResponse } from "@cpc/analyzer/lib/analyze-types";
import { expect, test, type Page, type Route } from "@playwright/test";
import { existsSync, readFileSync } from "node:fs";
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
   and Bhayshul Tuten. In norcal it is the recorded trade of AT-20: The Mean Machine gives Tyler Allgeier to
   Mitseeker5000 for Chris Olave and Devin Singletary, the two longest team names, so a long column label must fit.
   Another client takes its two longest team names, with one player given and two got. */
function stageTrade(teams: RawTeam[]): { team: number; with: number; give: string[]; get: string[] } {
  if (CLIENT === "cpc") return { team: 6, with: 12, give: ["8151"], get: ["6801", "12490"] };
  if (CLIENT === "norcal") return { team: 4, with: 6, give: ["8132"], get: ["8144", "6130"] };
  const [mine, theirs] = [...teams].filter((t) => t.players.length >= 2).sort((a, b) => b.team.length - a.team.length || a.roster_id - b.roster_id);
  return { team: mine.roster_id, with: theirs.roster_id, give: [mine.players[0].player_id], get: theirs.players.slice(0, 2).map((p) => p.player_id) };
}

/* The name of a team of the client. */
const teamName = (rosterId: number) => TEAMS.find((t) => t.roster_id === rosterId)!.team;

/* The row of a team on the stage of a hero. */
const rowOf = (page: Page, hero: string, team: string) =>
  page.locator(`${hero} [data-mesh-anchor]`).filter({ has: page.locator("[data-stage-team]").getByText(team, { exact: true }) });

/* The headshot tokens of a row: a face or the initials of a face that did not load. The "+N" token is not a face. */
const tokensOf = (row: ReturnType<typeof rowOf>) => row.locator("[data-mesh-hole][title]");

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

/* The analyzer with a stored passphrase, so no dialog covers the page. The teams route answers with the real rosters,
   and every other call off this machine fails, so no test reaches the live API. `onAnalyze` gets the held POST of the
   grade, so a test of the reveal can answer it when it chooses. `teamsAfterMs` holds the real rosters back for that
   long, as a cold teams route of the API does on a first load. */
async function openAnalyzer(page: Page, query = "", theme: Theme = "dark", onAnalyze?: (route: Route) => void, teamsAfterMs = 0) {
  await page.route((url) => !["127.0.0.1", "localhost"].includes(url.hostname), (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    // The grade and the search are held: the route answers the preflight and never answers the POST, so the wait
    // runs for as long as the test samples it. The page closes with the request still open.
    const held = path.endsWith("/analyze") || path.endsWith("/find-stream");
    if (held && request.method() === "OPTIONS") return route.fulfill({ status: 204, headers: CORS });
    if (held && path.endsWith("/analyze")) return onAnalyze?.(route);
    if (held) return;
    if (!path.endsWith("/teams")) return route.abort();
    if (request.method() === "OPTIONS") return route.fulfill({ status: 204, headers: CORS });
    const answer = () => route.fulfill({ status: 200, headers: CORS, contentType: "application/json", body: JSON.stringify({ teams: TEAMS }) });
    if (teamsAfterMs > 0) return void setTimeout(() => void answer().catch(() => undefined), teamsAfterMs);
    return answer();
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

/* Idle: the mesh holds still, and it pauses out of view and in a hidden tab. */
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

/* Idle: each hero text over the mesh reaches 4.5:1. The floor runs with motion off. The idle mesh is the same still mesh
   either way, so the pixel scan reads idle here. */
for (const theme of ["dark", "light"] as const) {
  for (const width of [390, 1280]) {
    test(`idle contrast: ${CLIENT} each hero text over the mesh reaches 4.5:1 with a trade on the stage, ${theme} ${width}px (AT-20)`, async ({ page }, info) => {
      const trade = stageTrade(TEAMS);
      await page.setViewportSize({ width, height: 900 });
      await openAnalyzer(page, `?team=${trade.team}&with=${trade.with}&give=${trade.give.join(",")}&get=${trade.get.join(",")}`, theme);
      const hero = page.locator(HERO);
      // Idle shows the count of each side, and the row label of each side is a hero text that the scan reads.
      await expect(rowOf(page, HERO, teamName(trade.team)).getByText(`${trade.get.length} players`)).toBeVisible();
      await expect(rowOf(page, HERO, teamName(trade.with)).getByText(`${trade.give.length} player`, { exact: true })).toBeVisible();
      await settle(page);
      await hero.screenshot({ path: info.outputPath(`idle-stage-${CLIENT}-${theme}-${width}.png`) });
      expect(await scanHeroPixels(page, HERO), `the idle hero of ${CLIENT} breaks the readability floor`).toEqual([]);
    });
  }
}

/* A side with no player yet shows a dashed empty token in place of a count. Its row label sits on the mesh with no
   count beside it, so it gets its own pixel scan. */
for (const width of [390, 1280]) {
  test(`idle contrast: ${CLIENT} the placeholder of a side with no player reaches 4.5:1, dark ${width}px (AT-20)`, async ({ page }, info) => {
    const trade = stageTrade(TEAMS);
    await page.setViewportSize({ width, height: 900 });
    await openAnalyzer(page, `?team=${trade.team}&with=${trade.with}&give=${trade.give.join(",")}`);
    const hero = page.locator(HERO);
    await expect(rowOf(page, HERO, teamName(trade.team)).locator("[data-stage-empty]")).toBeVisible();
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

/* The name of a player of a team of the client. */
const playerName = (rosterId: number, playerId: string) => TEAMS.find((t) => t.roster_id === rosterId)!.players.find((p) => p.player_id === playerId)!.name;

/*
 * Taps "Grade the Trade" and watches each token of the wait hero on each frame until `count` tokens are at rest: fully
 * opaque, with no move, no scale, and no blur. It gives the time in ms from the tap, whether a token ever moved or blurred,
 * and whether a token ever showed part faded.
 */
async function tapAndTimeTokens(page: Page, count: number): Promise<{ elapsed: number; moved: boolean; faded: boolean }> {
  const button = page.getByRole("button", { name: "Grade the Trade" });
  await expect(button).toBeEnabled();
  const handle = await button.elementHandle();
  return page.evaluate(
    ([el, hero, want]) =>
      new Promise<{ elapsed: number; moved: boolean; faded: boolean }>((done, fail) => {
        let moved = false;
        let faded = false;
        const start = performance.now();
        (el as HTMLElement).click();
        const check = () => {
          const elapsed = performance.now() - start;
          if (elapsed > 3000) return fail(new Error("the tokens did not come to rest within 3 s"));
          const tokens = [...document.querySelectorAll(`${hero} [data-mesh-hole][title]`)];
          let still = 0;
          for (const token of tokens) {
            const style = getComputedStyle(token);
            const m = new DOMMatrixReadOnly(style.transform === "none" ? undefined : style.transform);
            const shifted = Math.abs(m.f) > 0.01 || Math.abs(m.a - 1) > 0.001;
            const blurred = !["none", "blur(0px)"].includes(style.filter);
            const opacity = parseFloat(style.opacity);
            if (shifted || blurred) moved = true;
            if (opacity > 0 && opacity < 0.99) faded = true;
            if (!shifted && !blurred && opacity >= 0.99) still++;
          }
          if (tokens.length === want && still === want) return done({ elapsed, moved, faded });
          requestAnimationFrame(check);
        };
        requestAnimationFrame(check);
      }),
    [handle, WAIT_HERO, count] as const,
  );
}

/* Opens trade B of the spec in cpc. The query fills two sides: The Blue Tent gets 5 from Lil Fridge, and Lil Fridge gets
   Bucky Irving. The third side, All You Need Is Love, joins through "+", and its gets are picked in the sheets. */
async function openTradeB(page: Page) {
  await openAnalyzer(page, "?team=1&with=3&get=11560,1466,2449,3198,4034&give=11584");
  await page.getByRole("button", { name: "Add a team" }).click();
  await page.getByRole("dialog").getByRole("button", { name: /All You Need Is Love/ }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  const pick = async (side: string, from: string, names: string[]) => {
    await page.getByRole("button", { name: `Add a player ${side} gets` }).click();
    const sheet = page.getByRole("dialog");
    await sheet.getByRole("tab", { name: from }).click();
    for (const name of names) await sheet.getByRole("checkbox", { name: new RegExp(name) }).click();
    await sheet.getByRole("button", { name: /^Done/ }).click();
    await expect(page.getByRole("dialog")).toHaveCount(0);
  };
  await pick("Team Three", "The Blue Tent", ["Rashee Rice", "Brock Bowers"]);
  await pick("Team Two", "All You Need Is Love", ["Ashton Jeanty", "Jeremiyah Love"]);
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

/* Wait: the mesh weighs each side in turn. */
test.describe("the wait, with motion on", () => {
  test.use({ reducedMotion: "no-preference" });

  for (const width of [375, 768, 1280]) {
    test(`wait start: ${CLIENT} the mesh moves and "Weighing the sides" shows within 100 ms of the tap, ${width}px (AT-3)`, { tag: "@timing" }, async ({ page }, info) => {
      await page.setViewportSize({ width, height: 900 });
      await openAnalyzer(page, stageQuery());
      await settle(page);
      const elapsed = await tapAndTimeWait(page);
      console.log(`wait start: ${CLIENT} ${width}px: ${elapsed.toFixed(1)} ms from the tap`);
      await page.locator(WAIT_HERO).screenshot({ path: info.outputPath(`wait-start-${CLIENT}-${width}.png`) });
      expect(elapsed).toBeLessThanOrEqual(100);
    });
  }

  test(`wait status: ${CLIENT} the accessibility tree holds one status, "Grading the trade", at 2 s and at 7 s, 375px (AT-9)`, async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 900 });
    await openAnalyzer(page, stageQuery());
    await page.getByRole("button", { name: "Grade the Trade" }).click();
    await expect(page.locator(WAIT_HERO)).toBeVisible();
    for (const wait of [2000, 5000]) {
      await page.waitForTimeout(wait);
      const statuses = (await page.locator("body").ariaSnapshot()).split("\n").filter((line) => /^\s*- status\b/.test(line));
      console.log(`wait status: ${CLIENT}: ${statuses.map((line) => line.trim()).join(" | ")}`);
      expect(statuses.map((line) => line.trim())).toEqual(["- status: Grading the trade"]);
    }
  });

  test(`wait dips: ${CLIENT} the mesh dips under each side in turn, about 1.25 s each, 1280px, 8x CPU slowdown (AT-5)`, { tag: "@timing" }, async ({ browser }, info) => {
    // A page of its own records a video of the wait, which is the recording of AT-5.
    const context = await browser.newContext({
      viewport: { width: 1280, height: 900 },
      reducedMotion: "no-preference",
      recordVideo: { dir: info.outputPath("video"), size: { width: 1280, height: 900 } },
    });
    const page = await context.newPage();
    await openAnalyzer(page, stageQuery());
    await settle(page);
    // The slowdown stands in for the slow runner of CI, where a shot of the wait takes much longer than on a laptop.
    const cdp = await context.newCDPSession(page);
    await cdp.send("Emulation.setCPUThrottlingRate", { rate: 8 });
    await tapAndTimeWait(page);
    // The page samples the side that pulls hardest at each frame for 5 s, or -1 when no weight pulls, with the time of
    // the frame. The time comes from the page, so a slow shot from the test neither delays a sample nor skips one.
    const sampled = page.evaluate(
      (canvas) =>
        new Promise<{ at: number; side: number }[]>((done) => {
          const samples: { at: number; side: number }[] = [];
          const start = performance.now();
          const tick = (now: number) => {
            const el = document.querySelector<HTMLCanvasElement>(canvas);
            const pulls = (el?.dataset.meshPulls ?? "").split(",").filter(Boolean).map(Number);
            const top = Math.max(0, ...pulls);
            samples.push({ at: Math.round(now - start), side: top > 0.05 ? pulls.indexOf(top) : -1 });
            if (now - start < 5000) requestAnimationFrame(tick);
            else done(samples);
          };
          requestAnimationFrame(tick);
        }),
      WAIT_CANVAS,
    );
    // The test takes a shot at each of the first four dips, while the page samples.
    let shot = 0;
    let last = -1;
    const start = Date.now();
    while (Date.now() - start < 5000) {
      const now = await pulls(page);
      const top = Math.max(...now);
      const side = top > 0.05 ? now.indexOf(top) : -1;
      if (side >= 0 && side !== last && shot < 4) {
        await page.waitForTimeout(500);
        await page.locator(WAIT_HERO).screenshot({ path: info.outputPath(`wait-dip-${CLIENT}-${shot++}-side-${side}.png`) });
      }
      if (side >= 0) last = side;
      await page.waitForTimeout(40);
    }
    const samples = await sampled;
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
    // Each full turn in the middle of the sample holds about 1.25 s, from the first frame of one side to the first frame
    // of the next. The turn starts and ends at a small pull, so each side crosses the cut at the same place in its turn.
    for (const run of runs.slice(1, -1)) {
      const turn = runs[runs.indexOf(run) + 1].from - run.from;
      expect(turn, `side ${run.side} held the weight ${turn} ms`).toBeGreaterThan(1000);
      expect(turn, `side ${run.side} held the weight ${turn} ms`).toBeLessThan(1500);
    }
  });

  test(`wait frames: ${CLIENT} no frame of the wait takes longer than 50 ms after the first second, 375px, 4x CPU slowdown (AT-15)`, { tag: "@timing" }, async ({ page }, info) => {
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

  for (const width of [375, 768, 1280]) {
    test(`stage rise: ${CLIENT} the headshots of each side rise into its row within 1 s of the tap, ${width}px (AT-29)`, { tag: "@timing" }, async ({ page }, info) => {
      const trade = stageTrade(TEAMS);
      await page.setViewportSize({ width, height: 900 });
      await openAnalyzer(page, stageQuery());
      await settle(page);
      // Idle shows no face, only the count of each side.
      expect(await page.locator(`${HERO} [data-mesh-hole][title]`).count()).toBe(0);
      const { elapsed, moved } = await tapAndTimeTokens(page, trade.get.length + trade.give.length);
      console.log(`stage rise: ${CLIENT} ${width}px: the last token at rest ${elapsed.toFixed(0)} ms after the tap, moved ${moved}`);
      await page.locator(WAIT_HERO).screenshot({ path: info.outputPath(`stage-rise-${CLIENT}-${width}.png`) });
      expect(elapsed).toBeLessThanOrEqual(1000);
      expect(moved, "the tokens did not rise").toBe(true);
      // Each row holds the players its side gets, by name.
      const asker = await tokensOf(rowOf(page, WAIT_HERO, teamName(trade.team))).evaluateAll((els) => els.map((el) => el.getAttribute("title")));
      const other = await tokensOf(rowOf(page, WAIT_HERO, teamName(trade.with))).evaluateAll((els) => els.map((el) => el.getAttribute("title")));
      expect(asker).toEqual(trade.get.map((id) => playerName(trade.with, id)));
      expect(other).toEqual(trade.give.map((id) => playerName(trade.team, id)));
    });
  }

  test(`stage rise: ${CLIENT} on a cold load with slow teams, the headshots rise within 1 s of the tap and no line names a side title, 375px (AT-29)`, { tag: "@timing" }, async ({ page }) => {
    const trade = stageTrade(TEAMS);
    await page.setViewportSize({ width: 375, height: 900 });
    // The rosters arrive 2 s after the page opens. The reader taps "Grade the Trade" as soon as it turns on.
    await openAnalyzer(page, stageQuery(), "light", undefined, 2000);
    const { elapsed } = await tapAndTimeTokens(page, trade.get.length + trade.give.length);
    console.log(`stage rise cold: ${CLIENT}: the last token at rest ${elapsed.toFixed(0)} ms after the tap`);
    expect(elapsed).toBeLessThanOrEqual(1000);
    // The stage lines are fixed when the wait starts, so each named line names a real team, manager, or player.
    const lines = new Set<string>();
    for (let t = 0; t < 5600; t += 250) {
      const line = await page.locator(`${WAIT_HERO} .t-think-text:last-child`).textContent();
      if (line) lines.add(line);
      await page.waitForTimeout(250);
    }
    console.log(`stage rise cold: ${CLIENT}: lines ${[...lines].join(" / ")}`);
    expect([...lines].filter((line) => /Your Team|Team Two/.test(line))).toEqual([]);
    expect(lines.size).toBeGreaterThanOrEqual(3);
  });

  for (const width of [375, 768, 1280]) {
    test(`stage big: ${CLIENT} trade B shows 3 rows, and The Blue Tent shows 3 headshots and +2, ${width}px (AT-27)`, async ({ page }, info) => {
      test.skip(CLIENT !== "cpc", "trade B is a trade of cpc");
      await page.setViewportSize({ width, height: 900 });
      await openTradeB(page);
      await page.getByRole("button", { name: "Grade the Trade" }).click();
      await expect(page.locator(WAIT_HERO)).toBeVisible();
      await expect(page.locator(`${WAIT_HERO} [data-mesh-anchor]`)).toHaveCount(3);
      const tent = rowOf(page, WAIT_HERO, "The Blue Tent");
      await expect(tokensOf(tent)).toHaveCount(3);
      await expect(tent.getByText("+2", { exact: true })).toBeVisible();
      await lineAtRest(page);
      await page.locator(WAIT_HERO).screenshot({ path: info.outputPath(`stage-big-${CLIENT}-${width}.png`) });
      // No row wraps: each row keeps one line, as tall as its touch row.
      const heights = await page.locator(`${WAIT_HERO} [data-mesh-anchor]`).evaluateAll((els) => els.map((el) => el.getBoundingClientRect().height));
      console.log(`stage big: ${CLIENT} ${width}px: row heights ${heights.join(", ")}`);
      for (const h of heights) expect(h).toBeLessThan(60);
    });
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

  /* The stage line swaps at 2.5 s, so two reads of the canvas at 1 s and 3 s span a swap. The swap of the text sits
     over the canvas, so it may change the hero but never one pixel of the mesh. */
  for (const [theme, width] of [["light", 375], ["dark", 1280]] as const) {
    test(`wait still: ${CLIENT} the canvas keeps each pixel across a swap of the stage line, ${theme} ${width}px (AT-13)`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await openAnalyzer(page, stageQuery(), theme);
      await page.getByRole("button", { name: "Grade the Trade" }).click();
      const canvas = page.locator(WAIT_CANVAS);
      await expect(canvas).toBeVisible();
      const read = () =>
        canvas.evaluate((el) => {
          const c = el as HTMLCanvasElement;
          return Array.from(c.getContext("2d")!.getImageData(0, 0, c.width, c.height).data);
        });
      await page.waitForTimeout(1000);
      const first = await read();
      await page.waitForTimeout(2000);
      const second = await read();
      let differ = 0;
      for (let k = 0; k < first.length; k += 4) if (first.slice(k, k + 4).some((v, i) => v !== second[k + i])) differ++;
      console.log(`wait still: ${CLIENT} ${theme} ${width}px: ${differ} px differ of ${first.length / 4}`);
      expect(second.length).toBe(first.length);
      expect(differ, "the canvas changed in the wait with motion off").toBe(0);
    });
  }
});

test.describe("the stage, with motion off", () => {
  test(`stage fade: ${CLIENT} with reduced motion the headshots fade in and no token moves, 1280px (AT-29)`, async ({ page }, info) => {
    const trade = stageTrade(TEAMS);
    await page.setViewportSize({ width: 1280, height: 900 });
    await openAnalyzer(page, stageQuery());
    const { elapsed, moved, faded } = await tapAndTimeTokens(page, trade.get.length + trade.give.length);
    console.log(`stage fade: ${CLIENT}: the last token at rest ${elapsed.toFixed(0)} ms after the tap, moved ${moved}, faded ${faded}`);
    await page.locator(WAIT_HERO).screenshot({ path: info.outputPath(`stage-fade-${CLIENT}-1280.png`) });
    expect(moved, "a token moved with motion off").toBe(false);
    expect(faded, "the tokens showed with no fade").toBe(true);
  });
});

/* The read hero of the result, which holds the mesh of the reveal. */
const READ_HERO = 'section[aria-label="The Read"]';

/* The answer of the local API to the trade on the stage, recorded once from a real grade on 2026-11-17: trade T in cpc
   (Lean yes, 31 s) and the trade of stageTrade in norcal (Lean yes, 25 s). A test of the reveal plays it to the held
   grade, so the reveal runs on a real grade. No test makes up a grade, so a client with no recording fails.
   The local API had no TYPESAFE_API_KEY, so neither grade has a Jev answer. The read of the week 10 chart failed, so
   each answer lists "chart" as missing and shows the no-values note. */
const ANSWERS: Record<string, string> = { cpc: "analyze-trade-t.json", norcal: "analyze-trade-norcal.json" };
const STAGE_ANSWER = join(process.cwd(), "e2e", "fixtures", ANSWERS[CLIENT] ?? `analyze-trade-${CLIENT}.json`);
function stageAnswer(): { body: string; doc: AnalyzeResponse } {
  if (!existsSync(STAGE_ANSWER)) throw new Error(`no recorded answer of the stage trade at ${STAGE_ANSWER}: record one from the local API`);
  const body = readFileSync(STAGE_ANSWER, "utf8");
  return { body, doc: JSON.parse(body) as AnalyzeResponse };
}

/* The index of the favored side in the order of the read hero, the asker first, or null when no side is favored. */
function favoredIndex(doc: AnalyzeResponse): number | null {
  const roster = favoredSide(doc);
  if (roster === null) return null;
  const order = [...doc.trade.sides].sort((a, b) => Number(b.roster_id === doc.trade.asker) - Number(a.roster_id === doc.trade.asker));
  return order.findIndex((side) => side.roster_id === roster);
}

/* The time line of one reveal, in ms of the clock of the machine. Each part is the first frame at which it is at rest:
   fully opaque and with no move left. Each sample of the mesh holds the flash and the pull of each side at one frame. */
type Reveal = {
  lean: number | null;
  scale: number | null;
  case: number | null;
  tabs: number | null;
  mesh: { at: number; flash: number; pulls: number[] }[];
  // The opacity of the root of the result at each frame, for the plain fade of motion off.
  fade: number[];
  // The largest move in px of the Lean word at any frame.
  leanMove: number;
};

/* Starts a watch of the reveal in the page. It runs on each frame for 2.5 s after the read hero shows. */
const watchReveal = (page: Page) =>
  page.evaluate((hero) => {
    const w = window as unknown as { reveal: Promise<unknown> };
    w.reveal = new Promise((done) => {
      const t: Record<string, unknown> = { lean: null, scale: null, case: null, tabs: null, mesh: [], fade: [], leanMove: 0 };
      const mesh = t.mesh as { at: number; flash: number; pulls: number[] }[];
      const fade = t.fade as number[];
      let shown: number | null = null;
      // The opacity of an element as the eye sees it: its own times each box above it.
      const seen = (el: Element | null) => {
        let o = 1;
        for (let up = el; up; up = up.parentElement) o *= parseFloat(getComputedStyle(up).opacity);
        return el ? o : 0;
      };
      const matrix = (el: Element) => new DOMMatrixReadOnly(getComputedStyle(el).transform === "none" ? undefined : getComputedStyle(el).transform);
      // A recipe ends its blur at blur(0), which the browser computes as blur(0px), so either counts as sharp.
      const sharp = (el: Element) => ["none", "blur(0px)"].includes(getComputedStyle(el).filter);
      const still = (el: Element | null) => !!el && seen(el) >= 0.99 && Math.abs(matrix(el).f) < 0.5 && sharp(el);
      const mark = (key: string, ok: boolean) => {
        if (ok && t[key] === null) t[key] = Date.now();
      };
      const tick = () => {
        const now = Date.now();
        const read = document.querySelector(hero);
        if (read) {
          shown ??= now;
          const lean = read.querySelector('[data-stable-id="lean-word"]');
          if (lean) t.leanMove = Math.max(t.leanMove as number, Math.abs(matrix(lean).f));
          mark("lean", still(lean));
          const fill = read.querySelector('[data-reveal-part="scale"]');
          mark("scale", !!fill && seen(fill) >= 0.99 && matrix(fill).a >= 0.99);
          mark("case", still(read.querySelector(".t-stagger-line")));
          const tabs = document.querySelector('[role="tablist"][aria-label="The sides"]');
          mark("tabs", !!tabs && seen(tabs) >= 0.99 && sharp(tabs.closest(".t-skel-content") ?? tabs));
          const canvas = read.querySelector<HTMLCanvasElement>("canvas[data-hero-mesh]");
          if (canvas?.dataset.meshFlash !== undefined)
            mesh.push({ at: now, flash: Number(canvas.dataset.meshFlash), pulls: (canvas.dataset.meshPulls ?? "").split(",").filter(Boolean).map(Number) });
          fade.push(parseFloat(getComputedStyle(read.closest("[data-trade-key]") ?? read).opacity));
          if (now - shown > 2500) return done(t);
        }
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }, READ_HERO);

/* Starts a watch of the light of the read mesh in each row, in the page. Near the peak of the flash and near the deepest
   dip it sums the light of the canvas inside the box of each row, and 2.5 s after the read hero
   shows it sums the light of the flat mesh at rest. The light of a pixel is its color times its alpha. */
const watchRowLight = (page: Page) =>
  page.evaluate((hero) => {
    const w = window as unknown as { rowLight: Promise<unknown> };
    w.rowLight = new Promise((done) => {
      let shown: number | null = null;
      let best = { flash: 0, sums: [] as number[] };
      let deepest = { pull: 0, sums: [] as number[] };
      const sums = (canvas: HTMLCanvasElement) => {
        const origin = canvas.getBoundingClientRect();
        const scale = canvas.width / origin.width;
        const ctx = canvas.getContext("2d")!;
        return [...document.querySelectorAll(`${hero} [data-mesh-anchor]`)].map((row) => {
          const box = row.getBoundingClientRect();
          const x = Math.round((box.left - origin.left) * scale);
          const y = Math.round((box.top - origin.top) * scale);
          const data = ctx.getImageData(x, y, Math.round(box.width * scale), Math.round(box.height * scale)).data;
          let sum = 0;
          for (let k = 0; k < data.length; k += 4) sum += ((data[k] + data[k + 1] + data[k + 2]) * data[k + 3]) / 255;
          return sum;
        });
      };
      const tick = () => {
        const canvas = document.querySelector<HTMLCanvasElement>(`${hero} canvas[data-hero-mesh]`);
        if (canvas && canvas.width > 1) {
          shown ??= Date.now();
          const flash = Number(canvas.dataset.meshFlash ?? 0);
          const pull = Math.max(0, ...(canvas.dataset.meshPulls ?? "").split(",").filter(Boolean).map(Number));
          // A resize clears the canvas until the next frame, so of the frames near the peak, the brightest one counts.
          const total = (list: number[]) => list.reduce((a, b) => a + b, 0);
          if (flash > 0.5) {
            const now = sums(canvas);
            if (total(now) > total(best.sums)) best = { flash, sums: now };
          }
          if (pull > 0.45) {
            const now = sums(canvas);
            if (total(now) > total(deepest.sums)) deepest = { pull, sums: now };
          }
          if (Date.now() - shown > 2500) return done({ flash: best, dip: deepest, rest: sums(canvas) });
        }
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }, READ_HERO);

const rowLightOf = (page: Page) =>
  page.evaluate(() => (window as unknown as { rowLight: Promise<unknown> }).rowLight) as Promise<RowLight>;

/* The light of each row at the peak of the flash, at the deepest dip, and at rest. */
type RowLight = { flash: { flash: number; sums: number[] }; dip: { pull: number; sums: number[] }; rest: number[] };

const revealOf = (page: Page) => page.evaluate(() => (window as unknown as { reveal: Promise<unknown> }).reveal) as Promise<Reveal>;

/*
 * Opens the stage trade, taps "Grade the Trade", lets the wait run for 1.5 s, then answers the held grade with the
 * recorded answer of that trade. It gives the time the answer went out and the time line of the reveal.
 */
async function gradeAndReveal(page: Page, theme: Theme = "dark", alsoWatch?: (page: Page) => Promise<unknown>): Promise<{ sent: number; reveal: Reveal; doc: AnalyzeResponse }> {
  const { body, doc } = stageAnswer();
  let held: Route | undefined;
  await openAnalyzer(page, stageQuery(), theme, (route) => {
    held = route;
  });
  await settle(page);
  await page.getByRole("button", { name: "Grade the Trade" }).click();
  await expect(page.locator(WAIT_HERO)).toBeVisible();
  await expect.poll(() => held !== undefined).toBe(true);
  await page.waitForTimeout(1500);
  await watchReveal(page);
  await alsoWatch?.(page);
  // The clock starts before the answer goes out, so each time from it is an upper bound.
  const sent = Date.now();
  await held!.fulfill({ status: 200, headers: CORS, contentType: "application/json", body });
  return { sent, reveal: await revealOf(page), doc };
}

/* Each time of the reveal in ms from the answer, for the log of the evidence. */
const stamps = (sent: number, r: Reveal) =>
  (["lean", "scale", "case", "tabs"] as const).map((key) => `${key} ${r[key] === null ? "never" : `${r[key]! - sent} ms`}`).join(", ");

/* Reveal: the mesh flashes and dips toward the favored side, and the parts of the read land in order, in about 1 s. */
test.describe("the reveal, with motion on", () => {
  test.use({ reducedMotion: "no-preference" });

  for (const width of [375, 768, 1280]) {
    test(`reveal order: ${CLIENT} the Lean word lands first, then the scale, then the Case and the side tabs, within about 1 s, ${width}px (AT-10, AT-11)`, { tag: "@timing" }, async ({ browser }, info) => {
      // At 1280 px a page of its own records a video, which is the recording of AT-11 and AT-12.
      const context = await browser.newContext({
        viewport: { width, height: 900 },
        reducedMotion: "no-preference",
        ...(width === 1280 ? { recordVideo: { dir: info.outputPath("video"), size: { width, height: 900 } } } : {}),
      });
      const page = await context.newPage();
      const { sent, reveal } = await gradeAndReveal(page);
      await page.locator(READ_HERO).screenshot({ path: info.outputPath(`reveal-end-${CLIENT}-${width}.png`) });
      console.log(`reveal order: ${CLIENT} ${width}px: ${stamps(sent, reveal)}`);
      await context.close();
      if (width === 1280) console.log(`reveal order: ${CLIENT}: the recording is ${await page.video()?.path()}`);
      const { lean, scale, case: readCase, tabs } = reveal;
      for (const [part, at] of Object.entries({ lean, scale, case: readCase, tabs })) expect(at, `the ${part} never came to rest`).not.toBeNull();
      expect(lean! - sent, "the Lean word took too long after the answer").toBeLessThanOrEqual(1300);
      expect(lean!, "the scale came to rest before the Lean word").toBeLessThan(scale!);
      expect(scale!, "the Case came to rest before the scale").toBeLessThan(readCase!);
      expect(scale!, "the side tabs came to rest before the scale").toBeLessThan(tabs!);
      expect(Math.max(readCase!, tabs!) - sent, "the reveal took longer than about 1 s").toBeLessThanOrEqual(1300);
    });
  }

  test(`reveal mesh: ${CLIENT} the lines of the favored side flash once, then the mesh dips toward it and goes flat, 1280px (AT-12)`, async ({ page }, info) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    const { sent, reveal, doc } = await gradeAndReveal(page);
    const favored = favoredIndex(doc);
    const { mesh } = reveal;
    console.log(`reveal mesh: ${CLIENT}: Lean ${doc.lean}, favored side ${favored === null ? "none" : `${favored} (roster ${favoredSide(doc)})`}`);
    // The result hero holds the same rows as the wait, one anchor per side in the order of the read, the asker first.
    const order = [...doc.trade.sides].sort((a, b) => Number(b.roster_id === doc.trade.asker) - Number(a.roster_id === doc.trade.asker));
    await expect(page.locator(`${READ_HERO} [data-mesh-anchor] [data-stage-team]`)).toHaveText(order.map((side) => side.team));
    for (const side of order) await expect(tokensOf(rowOf(page, READ_HERO, side.team))).toHaveCount(Math.min(side.gets.length, 3));
    const peak = mesh.reduce((a, b) => (b.flash > a.flash ? b : a), mesh[0]);
    const pullOf = (i: number) => Math.max(...mesh.map((m) => m.pulls[i] ?? 0));
    const deepest = favored === null ? null : mesh.reduce((a, b) => ((b.pulls[favored] ?? 0) > (a.pulls[favored] ?? 0) ? b : a), mesh[0]);
    console.log(
      `reveal mesh: ${CLIENT}: flash peak ${peak.flash} at ${peak.at - sent} ms, ` +
        `${deepest ? `deepest dip ${deepest.pulls[favored!]} at ${deepest.at - sent} ms, ` : ""}last pulls ${mesh.at(-1)?.pulls.join(",")}`,
    );
    await page.locator(READ_HERO).screenshot({ path: info.outputPath(`reveal-flat-${CLIENT}-1280.png`) });
    expect(mesh.at(-1)!.pulls.every((p) => p === 0), "the mesh did not go flat").toBe(true);
    if (favored === null) {
      // A Gut call favors no side, so the mesh settles flat with no flash and no dip.
      expect(peak.flash).toBe(0);
      expect(mesh.every((m) => m.pulls.every((p) => p === 0))).toBe(true);
      return;
    }
    expect(peak.flash, "the favored side did not flash").toBeGreaterThan(0.5);
    expect(mesh.filter((m) => m.at > peak.at + 600).every((m) => m.flash === 0), "the flash did not fade in about 0.6 s").toBe(true);
    expect(peak.at, "the dip came before the flash").toBeLessThan(deepest!.at);
    expect(pullOf(favored), "the mesh did not dip toward the favored side").toBeGreaterThan(0.3);
    for (let i = 0; i < doc.trade.sides.length; i++) if (i !== favored) expect(pullOf(i), `the mesh dipped under side ${i}`).toBe(0);
  });

  /* The rows stack, so a light that spreads from the center of the favored row reaches the other row too. The flash and
     the light of the dip must stay in the region of the favored row. */
  for (const [theme, width] of [["light", 375], ["dark", 1280]] as const) {
    test(`reveal rows: ${CLIENT} the flash and the dip light only the row of the favored side, ${theme} ${width}px (AT-12)`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      const { doc } = await gradeAndReveal(page, theme, watchRowLight);
      const favored = favoredIndex(doc);
      test.skip(favored === null, "the recorded answer favors no side");
      const { flash, dip, rest } = await rowLightOf(page);
      const lit = (sums: number[]) => sums.map((sum, i) => Math.max(0, sum - rest[i]));
      const [flashLit, dipLit] = [lit(flash.sums), lit(dip.sums)];
      const other = flashLit.map((_, i) => i).filter((i) => i !== favored);
      console.log(
        `reveal rows: ${CLIENT} ${theme} ${width}px: favored row ${favored}; flash ${flash.flash} lights ${flashLit.map((v) => v.toFixed(0)).join(", ")}; ` +
          `dip ${dip.pull} lights ${dipLit.map((v) => v.toFixed(0)).join(", ")}`,
      );
      expect(flashLit[favored!], "the flash did not light the favored row").toBeGreaterThan(0);
      for (const i of other) {
        expect(flashLit[i], `the flash lit row ${i}`).toBeLessThan(0.15 * flashLit[favored!]);
        expect(dipLit[i], `the dip lit row ${i}`).toBeLessThan(0.25 * dipLit[favored!]);
      }
    });
  }

  /* The read hero sits on the mesh too, so the pixel scan reads it at the end of the reveal, with the mesh at rest. */
  for (const theme of ["dark", "light"] as const) {
    for (const width of [390, 1280]) {
      test(`reveal contrast: ${CLIENT} each hero text reaches 4.5:1 at the end of the reveal, ${theme} ${width}px (AT-20)`, async ({ page }, info) => {
        await page.setViewportSize({ width, height: 900 });
        await gradeAndReveal(page, theme);
        await lineAtRest(page);
        await page.locator(READ_HERO).screenshot({ path: info.outputPath(`reveal-contrast-${CLIENT}-${theme}-${width}.png`) });
        expect(await scanHeroPixels(page, READ_HERO), `the read hero of ${CLIENT} breaks the readability floor`).toEqual([]);
      });
    }
  }
});

test.describe("the reveal, with motion off", () => {
  test(`reveal still: ${CLIENT} the mesh stays still, no part moves, and the result shows in one plain fade, 1280px (AT-13)`, async ({ page }, info) => {
    await page.setViewportSize({ width: 1280, height: 900 });
    const { reveal } = await gradeAndReveal(page);
    await page.locator(READ_HERO).screenshot({ path: info.outputPath(`reveal-still-${CLIENT}-1280.png`) });
    console.log(`reveal still: ${CLIENT}: the opacity of the result over the first frames: ${reveal.fade.slice(0, 12).map((o) => o.toFixed(2)).join(", ")}`);
    expect(reveal.mesh.every((m) => m.flash === 0 && m.pulls.every((p) => p === 0)), "the mesh moved at the reveal with motion off").toBe(true);
    expect(reveal.leanMove, "the Lean word moved with motion off").toBeLessThan(0.5);
    expect(reveal.fade.some((o) => o < 0.99), "the result showed with no fade").toBe(true);
    expect(reveal.fade.at(-1)).toBe(1);
  });
});

/* Opens the stage trade and answers its grade at once with `body`, the recorded answer by default, then waits for the
   read hero. With motion off the result shows at rest, so a test reads its layout with no part in flight. */
async function gradeNow(page: Page, theme: Theme = "dark", body = stageAnswer().body) {
  await openAnalyzer(page, stageQuery(), theme, (route) => route.fulfill({ status: 200, headers: CORS, contentType: "application/json", body }));
  await page.getByRole("button", { name: "Grade the Trade" }).click();
  await expect(page.locator(READ_HERO)).toBeVisible();
  await expect(page.getByRole("tablist", { name: "The sides" })).toBeVisible();
}

/* The visible images and player chips of the page below the read hero. The hidden Stack keeps its rows for Edit, so a
   part that the reader cannot see does not count. */
const shownBelowHero = (page: Page) =>
  page.evaluate((hero) => {
    const read = document.querySelector(hero)!;
    const below = (el: Element) => !read.contains(el) && el.checkVisibility() && read.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING;
    return {
      images: [...document.querySelectorAll("main img")].filter(below).map((img) => img.getAttribute("src") ?? ""),
      chips: [...document.querySelectorAll("main li:has(> img)")].filter(below).length,
    };
  }, READ_HERO);

test.describe("the result, with motion off", () => {
  for (const width of [375, 768, 1280]) {
    for (const theme of ["light", "dark"] as const) {
      test(`result once: ${CLIENT} below the hero the result has no The Trade chapter, no player chip, no headshot, and no fold line, ${theme} ${width}px (AT-30)`, async ({ page }, info) => {
        await page.setViewportSize({ width, height: 900 });
        await gradeNow(page, theme);
        await page.screenshot({ path: info.outputPath(`result-once-${CLIENT}-${theme}-${width}.png`), fullPage: true });
        await expect(page.getByRole("heading", { name: "The Trade", exact: true })).toHaveCount(0);
        await expect(page.getByRole("group", { name: "The trade", exact: true })).toHaveCount(0);
        // Each side tab of the result, so no panel hides a list of players.
        for (const tab of await page.getByRole("tablist", { name: "The sides" }).getByRole("tab").all()) {
          await tab.click();
          const shown = await shownBelowHero(page);
          console.log(`result once: ${CLIENT} ${theme} ${width}px, tab ${await tab.textContent()}: ${shown.images.length} images, ${shown.chips} chips below the hero`);
          expect(shown.images, "an image shows below the hero").toEqual([]);
          expect(shown.chips, "a player chip shows below the hero").toBe(0);
        }
      });

      test(`result edit: ${CLIENT} Edit in the header of The Sides is 44 px or more on each side, and opens the Stack with the trade in view, ${theme} ${width}px (AT-31)`, async ({ page }, info) => {
        await page.setViewportSize({ width, height: 900 });
        await gradeNow(page, theme);
        const sides = page.getByRole("heading", { name: "The Sides", exact: true });
        const edit = page.getByRole("button", { name: "Edit the trade" });
        await edit.scrollIntoViewIfNeeded();
        const box = (await edit.boundingBox())!;
        const head = (await sides.boundingBox())!;
        console.log(`result edit: ${CLIENT} ${theme} ${width}px: the Edit target is ${box.width.toFixed(1)} x ${box.height.toFixed(1)} px`);
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
        // Edit sits at the right of the heading, on its line.
        expect(box.x).toBeGreaterThan(head.x + head.width);
        expect(box.y).toBeLessThan(head.y + head.height);
        expect(box.y + box.height).toBeGreaterThan(head.y);
        await sides.locator("..").screenshot({ path: info.outputPath(`result-edit-header-${CLIENT}-${theme}-${width}.png`) });

        await edit.click();
        const stack = page.getByRole("region", { name: "Who gets what" });
        await expect(stack).toBeInViewport();
        // The Stack holds trade T: each side lists the players it gets.
        const trade = stageTrade(TEAMS);
        for (const id of trade.get) await expect(stack.getByText(playerName(trade.with, id), { exact: true })).toBeVisible();
        for (const id of trade.give) await expect(stack.getByText(playerName(trade.team, id), { exact: true })).toBeVisible();
        await page.screenshot({ path: info.outputPath(`result-edit-stack-${CLIENT}-${theme}-${width}.png`) });
      });
    }
  }

  /* The recorded reasons of trade T fit in 3 lines, so the test puts the Case of the same real grade in the place of the
     reason of the asker, to get a reason past 3 lines. Each other part of the answer stays as recorded. */
  test(`result fold: ${CLIENT} a fairness reason past 3 lines shows 3 lines and More, and a tap shows it in full, 375px (AT-32)`, async ({ page }, info) => {
    await page.setViewportSize({ width: 375, height: 900 });
    const { doc } = stageAnswer();
    const asker = doc.fairness!.sides.find((side) => side.roster_id === doc.trade.asker)!;
    const long = { ...doc, fairness: { ...doc.fairness!, sides: doc.fairness!.sides.map((side) => (side === asker ? { ...side, reason: doc.case } : side)) } };
    await gradeNow(page, "dark", JSON.stringify(long));
    const card = page.locator(READ_HERO);
    const reason = card.locator("p").filter({ hasText: doc.case.slice(0, 40) }).last();
    const lines = (el: HTMLElement) => Math.round(el.getBoundingClientRect().height / parseFloat(getComputedStyle(el).lineHeight));
    await reason.scrollIntoViewIfNeeded();
    expect(await reason.evaluate(lines), "the folded reason is not 3 lines").toBe(3);
    const more = card.getByRole("button", { name: "More", exact: true });
    await expect(more).toBeVisible();
    await expect(more).toHaveAttribute("aria-expanded", "false");
    const target = (await more.boundingBox())!;
    expect(target.width).toBeGreaterThanOrEqual(44);
    expect(target.height).toBeGreaterThanOrEqual(44);
    // The short reason of the other side fits, so it shows no More.
    await expect(card.getByRole("button", { name: "More", exact: true })).toHaveCount(1);
    await reason.locator("..").screenshot({ path: info.outputPath(`result-fold-before-${CLIENT}-375.png`) });

    await more.click();
    await expect(more).toHaveCount(0);
    const open = await reason.evaluate((el) => ({ lines: Math.round(el.getBoundingClientRect().height / parseFloat(getComputedStyle(el).lineHeight)), clipped: el.scrollHeight > el.clientHeight + 1 }));
    console.log(`result fold: ${CLIENT} 375px: the open reason runs ${open.lines} lines`);
    expect(open.lines).toBeGreaterThan(3);
    expect(open.clipped, "the open reason is still cut off").toBe(false);
    await reason.locator("..").screenshot({ path: info.outputPath(`result-fold-after-${CLIENT}-375.png`) });
  });
});
