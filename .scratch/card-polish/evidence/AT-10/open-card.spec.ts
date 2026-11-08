/**
 * The browser checks of the Open card on the static export in out/ of CLIENT=cpc: find-in-page on a closed card, and the frame rate of an open.
 * Run them after CLIENT=cpc pnpm build, with pnpm check:open-card. The frame rate is evidence for ADR 0028 and no gate of CI.
 */
import { expect, test } from "@playwright/test";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { serveDir } from "./serve";

// pnpm runs each script of the site in apps/site, so the export sits in out/ there.
const OUT = join(process.cwd(), "out");
// The week of the acceptance tests of card-polish, and its game of All You Need Is Love vs Unsolicited Dak Picks.
const ROUTE = "/2026/week-08/";
const GAME = 4;
// The CPU throttle of the slow phone of AT-10, as a slowdown factor of Chromium.
const THROTTLE = 4;
// The frames after the tap that the check counts. The open takes 0.45s and the blur ends a beat after it.
const WINDOW_MS = 800;

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  if (!existsSync(OUT)) throw new Error(`${OUT} does not exist. Run CLIENT=cpc pnpm build first.`);
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

/* The last words of the recap of the game, from the built page JSON. The pipeline rewrites recaps, so the test never holds them as a literal. */
function recapWords(): string {
  const page = JSON.parse(readFileSync(join(OUT, ROUTE, "page.json"), "utf8")) as { matchups: { id: number; recap: string | null }[] };
  const recap = page.matchups.find((matchup) => matchup.id === GAME)?.recap;
  if (!recap) throw new Error(`game ${GAME} of ${ROUTE} has no recap`);
  return recap.replace(/[.!?]$/, "").split(" ").slice(-6).join(" ");
}

test("find-in-page finds a word of a closed recap, and the match opens the card (AT-8)", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  // A text fragment runs the find of the browser on load, the same search as find-in-page.
  const words = recapWords();
  await page.goto(`${server.url}${ROUTE}#:~:text=${encodeURIComponent(words)}`);
  const head = page.locator(`button[aria-controls="recap-${GAME}"]:not([aria-label])`);
  await expect(head).toHaveAttribute("aria-expanded", "true");
  await expect(page.locator(`#recap-${GAME}`)).not.toHaveAttribute("hidden", /.*/);
  console.log(`find: "${words}" opened recap-${GAME}`);
});

test("the open of a game card keeps its frame rate on a slow phone (AT-10)", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto(`${server.url}${ROUTE}`);
  const head = page.locator(`button[aria-controls="recap-${GAME}"]:not([aria-label])`);
  await head.scrollIntoViewIfNeeded();
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Emulation.setCPUThrottlingRate", { rate: THROTTLE });
  // The page counts the frames from the tap, so the count holds no time of the test runner.
  const frames = page.evaluate(
    (windowMs) =>
      new Promise<number[]>((resolve) => {
        const stamps: number[] = [];
        const start = performance.now();
        const step = (now: number) => {
          stamps.push(now);
          if (now - start < windowMs) requestAnimationFrame(step);
          else resolve(stamps.slice(1).map((stamp, index) => stamp - stamps[index]));
        };
        requestAnimationFrame(step);
      }),
    WINDOW_MS,
  );
  await head.click();
  const gaps = (await frames).sort((a, b) => a - b);
  await cdp.send("Emulation.setCPUThrottlingRate", { rate: 1 });
  const median = gaps[Math.floor(gaps.length / 2)];
  const fps = Math.round(1000 / median);
  console.log(`frame rate: median ${fps} fps over ${gaps.length} frames, throttle ${THROTTLE}x, viewport 375px, worst gap ${gaps.at(-1)?.toFixed(1)} ms`);
  await expect(head).toHaveAttribute("aria-expanded", "true");
  // ADR 0028 keeps the blur while the median is 50 fps or more.
  expect(fps).toBeGreaterThanOrEqual(50);
});
