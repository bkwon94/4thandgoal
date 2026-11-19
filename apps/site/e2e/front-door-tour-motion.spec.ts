/**
 * The motion of the Tour of the front door on the static export in out/ of the current CLIENT, in WebKit, as Safari runs.
 * With motion on, the hole and the card glide together, and a burst of scroll leaves the card shown. Under reduced motion,
 * the hole jumps and the card only fades.
 */
import { type Page, chromium, devices, expect, test } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { samplesWhenStill, startSamples } from "./door-motion";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
// The client build writes the hidden /ask/ route only while the flag front_door is off. Then / is the home page.
const DOOR = existsSync(join(OUT, "ask", "index.html")) ? "/ask/" : "/";
const BO_GIRDS = "6";
const ASK_LINE = "Type any question about your team or your league, such as start or sit, a trade, or the playoff race.";

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
type Sample = { hole: Rect; card: Rect; opacity: number; scale: number; filters: number; header: string };

/* A browser with Your team, a kept passphrase, and no seen key. Each call off the test server fails, because the run
   uses no real API. The test waits until the hole and the card of Stop 1 hold still. */
async function openTour(page: Page) {
  await page.route((url) => url.hostname !== "127.0.0.1", (route) => route.abort());
  await page.addInitScript((team) => {
    localStorage.setItem("cpc.passphrase", "test");
    localStorage.setItem("cpc.your-team", team);
    // A kept team lets the season-sim Announcement open first and cover the page, so the setup marks it seen.
    localStorage.setItem("cpc.announcement.season-sim-2026", "seen");
  }, BO_GIRDS);
  await page.goto(`${server.url}${DOOR}`);
  await expect(page.getByRole("dialog", { name: "Suggestions" })).toBeVisible();
  await startSamples(page, readFrame);
  await samplesWhenStill(page);
}

/* One frame of the Tour as the reader sees it: the box of the hole and of the card, the opacity of the card times the
   opacity of each part around it, the largest scale on the card or a part around it, the count of the parts of the card
   with a filter, and the header. The function runs in the page, so it uses no value of the test. */
function readFrame() {
  const rect = (el: Element) => {
    const r = el.getBoundingClientRect();
    return { x: r.x, y: r.y, width: r.width, height: r.height };
  };
  const card = document.querySelector("[data-tour-card]")!;
  let opacity = 1;
  let scale = 1;
  for (let node: Element | null = card; node; node = node.parentElement) {
    const style = getComputedStyle(node);
    opacity *= Number(style.opacity);
    const matrix = new DOMMatrix(style.transform === "none" ? undefined : style.transform);
    const own = Math.hypot(matrix.a, matrix.b) * (style.scale === "none" ? 1 : Number(style.scale.split(" ")[0]));
    if (Math.abs(own - 1) > Math.abs(scale - 1)) scale = own;
  }
  const filters = [card, ...card.querySelectorAll("*")].filter((node) => !["none", ""].includes(getComputedStyle(node).filter)).length;
  const header = card.querySelector("h2, h3, [id]")?.textContent ?? "";
  // The clock time of this sample goes in a list beside the samples, at the same index, so a sample that holds still
  // stays equal to the one before it. A new list of samples starts a new list of times.
  const store = window as unknown as { doorSamples: unknown[]; tourTimesOf?: unknown[]; tourTimes: number[] };
  if (store.tourTimesOf !== store.doorSamples) {
    store.tourTimesOf = store.doorSamples;
    store.tourTimes = [];
  }
  store.tourTimes[store.doorSamples.length] = performance.now();
  return {
    hole: rect(document.querySelector("[data-tour-hole]")!),
    card: rect(card),
    opacity: Math.round(opacity * 100) / 100,
    scale: Math.round(scale * 1000) / 1000,
    filters,
    header,
  };
}

/* The offset of the card from the hole: the gap between the near edges, and the gap between the two centers across. */
function offsetOf({ hole, card }: Sample) {
  const below = card.y + card.height / 2 > hole.y + hole.height / 2;
  return {
    below,
    gap: below ? card.y - (hole.y + hole.height) : hole.y - (card.y + card.height),
    across: card.x + card.width / 2 - (hole.x + hole.width / 2),
  };
}

/* A slow runner, such as a CI machine, draws a frame only every so often. This init script blocks the main thread for
   `ms` at the first callback of each frame, so the Mac draws few frames in the glide, as CI does. The callbacks of one
   frame share one timestamp, so each frame is blocked once, and the frames come at an even pace. */
async function slowFrames(page: Page, ms: number) {
  await page.addInitScript((block) => {
    const raf = window.requestAnimationFrame.bind(window);
    let blocked = -1;
    window.requestAnimationFrame = (callback) =>
      raf((time) => {
        if (time !== blocked) {
          blocked = time;
          const end = performance.now() + block;
          while (performance.now() < end);
        }
        callback(time);
      });
  }, ms);
}

/* A loaded runner can stall for a few frames just as the glide starts. This init script waits until the Tour marks the
   control of Stop 2, and then blocks the main thread for `ms` at the first callback of each of the next 3 frames. So the
   frames of the glide come late on each run. The block reads Date.now, so a clock of the page does not move it. */
async function lateGlideFrames(page: Page, ms: number) {
  await page.addInitScript((block) => {
    const raf = window.requestAnimationFrame.bind(window);
    let marks = 0;
    let left = 0;
    let blocked = -1;
    new MutationObserver((records) => {
      for (const record of records) {
        if ((record.target as Element).hasAttribute("data-tour-target") && ++marks === 2) left = 3;
      }
    }).observe(document, { attributes: true, subtree: true, attributeFilter: ["data-tour-target"] });
    window.requestAnimationFrame = (callback) =>
      raf((time) => {
        if (left > 0 && time !== blocked) {
          blocked = time;
          left -= 1;
          const end = Date.now() + block;
          while (Date.now() < end);
        }
        callback(time);
      });
  }, ms);
}

/* AT-15: tap Next on Stop 1 and check each frame of the move to Stop 2. */
async function glideTogether(page: Page) {
  await openTour(page);
  await startSamples(page, readFrame);
  await page.getByRole("dialog", { name: "Suggestions" }).getByRole("button", { name: "Next" }).click();
  await expect(page.getByRole("dialog", { name: "Ask" })).toBeVisible();
  const samples = await samplesWhenStill<Sample>(page);
  const times = await page.evaluate((count) => (window as unknown as { tourTimes: number[] }).tourTimes.slice(0, count), samples.length);
  // The evidence of AT-15 is the frame samples, so the log prints each one with its clock time from the first sample.
  console.log(`AT-15 frame samples:\n${samples.map((sample, index) => `${index} ${(times[index] - times[0]).toFixed(1)} ms ${JSON.stringify({ ...sample, offset: offsetOf(sample) })}`).join("\n")}`);
  const first = samples[0];
  const last = samples.at(-1)!;
  const rest = offsetOf(first);
  const sideChange = offsetOf(last).below !== rest.below;
  /* The glide shows the hole at places between the two Stops, so the move is not a jump. The test reads clock time,
     not a count of frames, because a slow runner draws few frames in the 450 ms of the glide. A frame shows on the
     screen until the next frame, so each sample between the Stops counts the time up to the next sample. A jump puts
     the hole at the new Stop in its first frame, so no sample sits between the Stops and the time is 0. The place at
     rest and the place of a jump are exact, so a place more than 0.5 px from both is a real place of the glide. */
  const away = (hole: Rect) => Math.min(Math.hypot(hole.x - first.hole.x, hole.y - first.hole.y), Math.hypot(hole.x - last.hole.x, hole.y - last.hole.y));
  const betweenMs = samples.reduce((sum, { hole }, index) => (index + 1 < samples.length && away(hole) > 0.5 ? sum + times[index + 1] - times[index] : sum), 0);
  const tops = samples.map(({ hole }, index) => `${Math.round(hole.y)}@${Math.round(times[index] - times[0])}`).join(", ");
  console.log(`AT-15 time of the hole between the Stops: ${betweenMs.toFixed(1)} ms`);
  expect(betweenMs, `the hole shows between the Stops for 80 ms or more; the hole tops at each ms: ${tops}`).toBeGreaterThanOrEqual(80);
  // On a change of side the card fades out first, so each frame up to the first frame of that fade counts.
  const shown = sideChange ? samples.slice(0, samples.findIndex((sample) => sample.opacity < 0.99)) : samples;
  if (!sideChange) {
    expect(Math.min(...samples.map((sample) => sample.opacity)), "the card stays shown on a move with no change of side").toBeGreaterThanOrEqual(0.99);
  }
  const drift = shown.map((sample) => {
    const now = offsetOf(sample);
    return Math.max(Math.abs(now.gap - rest.gap), Math.abs(now.across - rest.across));
  });
  console.log(`AT-15 samples: ${samples.length}, side change: ${sideChange}, compared: ${shown.length}, largest drift: ${Math.max(...drift).toFixed(2)} px`);
  for (const [index, value] of drift.entries()) {
    expect(value, `frame ${index}: the card drifts ${value.toFixed(2)} px from its offset at rest`).toBeLessThanOrEqual(2);
  }
  // At the end the card sits at its offset again, on the side of the new Stop.
  const end = offsetOf(last);
  expect(Math.abs(end.gap - rest.gap), "the card ends at the same gap from the hole").toBeLessThanOrEqual(2);
  expect(last.opacity, "the card shows at the end").toBe(1);
}

test.describe("iPhone 390x660 with motion on", () => {
  const { defaultBrowserType: _browser, ...iphone } = devices["iPhone 15"];
  test.use({ ...iphone, viewport: { width: 390, height: 660 }, reducedMotion: "no-preference" });

  test("the hole and the card glide together from Stop 1 to Stop 2, until the card changes side (AT-15)", async ({ page }) => {
    await glideTogether(page);
  });

  test("on a slow runner with 150 ms frames, the hole and the card still glide together (AT-15)", async ({ page }) => {
    await slowFrames(page, 150);
    await glideTogether(page);
  });

  test("when the first frames of the glide come 400 ms late, the hole and the card still glide together (AT-15)", async ({ page }) => {
    await lateGlideFrames(page, 400);
    await glideTogether(page);
  });

  test("on a change of side from Stop 3 to Stop 4, the card fades out, holds its place, and fades back in once the hole lands", async ({ page }) => {
    await openTour(page);
    for (const name of ["Suggestions", "Ask"]) {
      await page.getByRole("dialog", { name }).getByRole("button", { name: "Next" }).click();
    }
    await expect(page.getByRole("dialog", { name: "Your team" })).toBeVisible();
    await samplesWhenStill(page);
    await startSamples(page, readFrame);
    await page.getByRole("dialog", { name: "Your team" }).getByRole("button", { name: "Next" }).click();
    await expect(page.getByRole("dialog", { name: "Menu" })).toBeVisible();
    const samples = await samplesWhenStill<Sample>(page);
    const first = samples[0];
    const last = samples.at(-1)!;
    expect(offsetOf(first).below, "the card sits over the team switch").toBe(false);
    expect(offsetOf(last).below, "the card sits under the menu button").toBe(true);
    // Each frame before the hole lands shows the card at its old place, or the card out of sight.
    const landed = samples.findIndex(({ hole }) => Math.abs(hole.y - last.hole.y) <= 0.5 && Math.abs(hole.x - last.hole.x) <= 0.5);
    const strays = samples
      .slice(0, landed)
      .filter(({ card, opacity }) => opacity > 0.01 && (Math.abs(card.x - first.card.x) > 1 || Math.abs(card.y - first.card.y) > 1));
    expect(strays, "the card moves while it shows, before the hole lands").toEqual([]);
    expect(Math.min(...samples.map((sample) => sample.opacity)), "the card fades out").toBeLessThanOrEqual(0.01);
    expect(last.opacity, "the card shows at the end").toBe(1);
  });
});

/* Short scrolls down and back. The control crosses the middle line of the screen, so the side of the card flips. A
   pause near the fade of the card lets the card fade out, and the scroll back flips the side again before the card
   comes back. The pause that does it moves with the load of the machine, so the test steps through the pauses around
   the fade. After each scroll the card must show again within 3 s, beside its hole, and never over its control. */
async function cardShowsAfterScrollBursts(page: Page) {
  for (let pause = 120; pause <= 220; pause += 5) {
    await page.evaluate(async (wait) => {
      window.scrollTo(0, 60);
      await new Promise((done) => setTimeout(done, wait));
      window.scrollTo(0, 0);
    }, pause);
    await expect
      .poll(() => page.evaluate(readFrame).then(({ opacity }) => opacity), { message: `the card shows again after a scroll with a pause of ${pause} ms`, timeout: 3000 })
      .toBe(1);
    const frame: Sample = await page.evaluate(readFrame);
    const { below, gap } = offsetOf(frame);
    // The card sits under a control in the top half of the screen and over a control in the bottom half.
    const holeInTopHalf = frame.hole.y + frame.hole.height / 2 <= page.viewportSize()!.height / 2;
    console.log(`E1 card at rest after a scroll with a pause of ${pause} ms: ${JSON.stringify({ hole: frame.hole, card: frame.card, opacity: frame.opacity, below, gap })}`);
    expect(below, `the card takes the side of its control after a pause of ${pause} ms`).toBe(holeInTopHalf);
    expect(gap, `the card does not cover its control after a pause of ${pause} ms`).toBeGreaterThanOrEqual(0);
  }
}

test.describe("a burst of scroll at phone width with motion on", () => {
  const { defaultBrowserType: _browser, ...iphone } = devices["iPhone 15"];
  test.use({ ...iphone, viewport: { width: 390, height: 660 }, reducedMotion: "no-preference" });

  test("WebKit 390x660: the card shows again beside its hole", async ({ page }) => {
    await openTour(page);
    await cardShowsAfterScrollBursts(page);
  });

  // The file runs in WebKit, so this test launches its own Chromium.
  test("Chromium 375x900: the card shows again beside its hole", async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage({ viewport: { width: 375, height: 900 }, reducedMotion: "no-preference" });
    await openTour(page);
    await cardShowsAfterScrollBursts(page);
    await browser.close();
  });
});

test.describe("iPhone 375x660 under reduced motion", () => {
  const { defaultBrowserType: _browser, ...iphone } = devices["iPhone 15"];
  test.use({ ...iphone, viewport: { width: 375, height: 660 }, reducedMotion: "reduce" });

  test("the hole jumps from the Suggestions to the ask box, and Stop 2 shows its full copy (AT-20)", async ({ page }) => {
    await openTour(page);
    await startSamples(page, readFrame);
    await page.getByRole("dialog", { name: "Suggestions" }).getByRole("button", { name: "Next" }).click();
    const stop = page.getByRole("dialog", { name: "Ask" });
    await expect(stop).toBeVisible();
    const samples = await samplesWhenStill<Sample>(page);
    console.log(`AT-20 frame samples of the hole:\n${samples.map((sample, index) => `${index} ${JSON.stringify({ hole: sample.hole, header: sample.header })}`).join("\n")}`);
    const from = samples[0].hole;
    const to = samples.at(-1)!.hole;
    const near = (a: Rect, b: Rect) => Math.abs(a.x - b.x) <= 1 && Math.abs(a.y - b.y) <= 1 && Math.abs(a.width - b.width) <= 1 && Math.abs(a.height - b.height) <= 1;
    const between = samples.filter(({ hole }) => !near(hole, from) && !near(hole, to));
    console.log(`AT-20 samples: ${samples.length}, frames between the Stops: ${between.length}`);
    expect(between, "no frame shows the hole between the Suggestions and the ask box").toEqual([]);
    await expect(stop).toContainText("Ask");
    await expect(stop).toContainText("2 of 4");
    await expect(stop).toHaveAccessibleDescription(ASK_LINE);
    await expect(stop.getByText(ASK_LINE)).toBeVisible();
  });

  test("the card swaps with no blur and no scale (AT-21)", async ({ page }) => {
    await openTour(page);
    await startSamples(page, readFrame);
    await page.getByRole("dialog", { name: "Suggestions" }).getByRole("button", { name: "Next" }).click();
    await expect(page.getByRole("dialog", { name: "Ask" })).toBeVisible();
    const samples = await samplesWhenStill<Sample>(page);
    console.log(`AT-21 frame samples of filter and transform:\n${samples.map((sample, index) => `${index} ${JSON.stringify({ filters: sample.filters, scale: sample.scale, opacity: sample.opacity, header: sample.header })}`).join("\n")}`);
    const filters = Math.max(...samples.map((sample) => sample.filters));
    const scales = [...new Set(samples.map((sample) => sample.scale))];
    console.log(`AT-21 samples: ${samples.length}, most parts with a filter: ${filters}, scales: ${scales.join(", ")}`);
    expect(filters, "no part of the card has a filter").toBe(0);
    expect(scales, "the card keeps a scale of 1").toEqual([1]);
  });
});
