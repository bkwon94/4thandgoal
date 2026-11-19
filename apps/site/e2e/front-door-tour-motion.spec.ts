/**
 * The motion of the Tour of the front door on the static export in out/ of the current CLIENT, in WebKit, as Safari runs.
 * With motion on, the hole and the card glide together. Under reduced motion, the hole jumps and the card only fades.
 */
import { type Page, devices, expect, test } from "@playwright/test";
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

test.describe("iPhone 390x660 with motion on", () => {
  const { defaultBrowserType: _browser, ...iphone } = devices["iPhone 15"];
  test.use({ ...iphone, viewport: { width: 390, height: 660 }, reducedMotion: "no-preference" });

  test("the hole and the card glide together from Stop 1 to Stop 2, until the card changes side (AT-15)", async ({ page }) => {
    await openTour(page);
    await startSamples(page, readFrame);
    await page.getByRole("dialog", { name: "Suggestions" }).getByRole("button", { name: "Next" }).click();
    await expect(page.getByRole("dialog", { name: "Ask" })).toBeVisible();
    const samples = await samplesWhenStill<Sample>(page);
    // The evidence of AT-15 is the frame samples, so the log prints each one.
    console.log(`AT-15 frame samples:\n${samples.map((sample, index) => `${index} ${JSON.stringify({ ...sample, offset: offsetOf(sample) })}`).join("\n")}`);
    const first = samples[0];
    const last = samples.at(-1)!;
    const rest = offsetOf(first);
    const sideChange = offsetOf(last).below !== rest.below;
    // The glide shows the hole at places between the two Stops, so the move is not a jump.
    const between = samples.filter(({ hole }) => Math.min(Math.abs(hole.y - first.hole.y), Math.abs(hole.y - last.hole.y)) > 2);
    expect(between.length, `the hole tops: ${samples.map(({ hole }) => Math.round(hole.y)).join(", ")}`).toBeGreaterThanOrEqual(3);
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
