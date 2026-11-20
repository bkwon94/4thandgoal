/**
 * The menu sheet at the size of an iPhone, in WebKit, on the static export in out/ of the current CLIENT, with motion on.
 * A tap on "Past weeks" opens and closes the list of weeks, and the top edge of the sheet stays still on each frame.
 * A second test holds each tap for some frames, as a slow CI runner does, so the motion of the list starts late.
 */
import { type Page, expect, test } from "@playwright/test";
import { join } from "node:path";
import { samplesWhenStill, startSamples } from "./door-motion";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");

// The browser of a file is set at its top, because a group cannot pick the browser. iOS Safari runs on WebKit.
test.use({
  browserName: "webkit",
  viewport: { width: 390, height: 660 },
  reducedMotion: "no-preference",
});

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

/* The top edge of the menu sheet and the height of the list of weeks, in px, as the page lays them out on this frame. */
const readSheet = () => ({
  top: document
    .querySelector("[data-menu-sheet]:not([data-slot='drawer-backdrop'])")!
    .getBoundingClientRect().top,
  list: document.querySelector(".menu-past")!.getBoundingClientRect().height,
});

/* Hold each tap on "Past weeks" for `frames` frames before the page gets it. A slow CI runner starts the motion of the
   list late after the tap, and this makes that late start the same on each run. The page code does not change. */
async function holdPastTaps(page: Page, frames: number) {
  await page.evaluate((frames) => {
    const replays = new WeakSet<Event>();
    window.addEventListener(
      "click",
      (event) => {
        const button = (event.target as Element).closest("button");
        if (replays.has(event) || button?.textContent?.trim() !== "Past weeks") return;
        event.stopImmediatePropagation();
        let left = frames;
        const wait = () => {
          if (left-- > 0) return requestAnimationFrame(wait);
          const replay = new MouseEvent("click", { bubbles: true, cancelable: true });
          replays.add(replay);
          button.dispatchEvent(replay);
        };
        requestAnimationFrame(wait);
      },
      true,
    );
  }, frames);
}

/* Tap "Past weeks", wait for the list of weeks to move, sample the sheet on each frame until it stands still, and return
   the samples. The one loop of startSamples keeps on, and each tap only clears its samples. A second loop would push
   two samples per frame, so the 20 still samples would be only 10 frames. The wait for the move keeps the still frames
   before a late motion out of the still check. */
async function togglePast(page: Page, expanded: boolean) {
  const button = page.getByRole("button", { name: "Past weeks" });
  const listHeight = () =>
    page.evaluate(() => document.querySelector(".menu-past")!.getBoundingClientRect().height);
  const before = await listHeight();
  await page.evaluate(() => {
    (window as unknown as { doorSamples: unknown[] }).doorSamples = [];
  });
  await button.click();
  await expect(button).toHaveAttribute("aria-expanded", String(expanded));
  await expect.poll(listHeight).not.toBe(before);
  return samplesWhenStill<{ top: number; list: number }>(page);
}

/* Open the menu sheet, wait for its drop to end, then open and close "Past weeks". Each tap waits `hold` frames. */
async function checkTopEdge(page: Page, hold: number) {
  await page.route(
    (url) => url.hostname !== "127.0.0.1",
    (route) => route.abort(),
  );
  await page.goto(`${server.url}/rankings/`);
  await page.getByRole("button", { name: "Open the menu" }).click();
  const sheet = page.locator("[data-menu-sheet]:not([data-slot='drawer-backdrop'])");
  await expect(sheet).toBeVisible();
  // Wait for the drop of the sheet to end, so the samples hold only the motion of "Past weeks".
  await startSamples(page, readSheet);
  const rest = (await samplesWhenStill<{ top: number; list: number }>(page)).at(-1)!.top;
  if (hold > 0) await holdPastTaps(page, hold);

  for (const step of ["opens", "closes"]) {
    const samples = await togglePast(page, step === "opens");
    const lists = samples.map((sample) => sample.list);
    // The list of weeks moves, so the samples hold the frames of the motion.
    expect(
      Math.max(...lists) - Math.min(...lists),
      `the list of weeks grows or shrinks as Past weeks ${step}`,
    ).toBeGreaterThan(20);
    const drift = Math.max(...samples.map((sample) => Math.abs(sample.top - rest)));
    expect(
      drift,
      `the top edge of the menu sheet moves ${drift}px as Past weeks ${step}`,
    ).toBeLessThanOrEqual(1);
  }
}

test("the top edge of the menu sheet stays still while Past weeks opens and closes", async ({
  page,
}) => {
  await checkTopEdge(page, 0);
});

test("the top edge of the menu sheet stays still when the motion of Past weeks starts late", async ({
  page,
}) => {
  // 30 frames is about 0.5 s, more than the 20 still frames that samplesWhenStill waits for.
  await checkTopEdge(page, 30);
});
