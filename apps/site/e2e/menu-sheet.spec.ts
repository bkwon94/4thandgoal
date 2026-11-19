/**
 * The menu sheet at the size of an iPhone, in WebKit, on the static export in out/ of the current CLIENT, with motion on.
 * A tap on "Past weeks" opens and closes the list of weeks, and the top edge of the sheet stays still on each frame.
 */
import { type Page, expect, test } from "@playwright/test";
import { join } from "node:path";
import { samplesWhenStill, startSamples } from "./door-motion";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");

// The browser of a file is set at its top, because a group cannot pick the browser. iOS Safari runs on WebKit.
test.use({ browserName: "webkit", viewport: { width: 390, height: 660 }, reducedMotion: "no-preference" });

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

/* The top edge of the menu sheet and the height of the list of weeks, in px, as the page lays them out on this frame. */
const readSheet = () => ({
  top: document.querySelector("[data-menu-sheet]:not([data-slot='drawer-backdrop'])")!.getBoundingClientRect().top,
  list: document.querySelector(".menu-past")!.getBoundingClientRect().height,
});

/* Tap "Past weeks", sample the sheet on each frame until it stands still, and return the samples. */
async function togglePast(page: Page) {
  await startSamples(page, readSheet);
  await page.getByRole("button", { name: "Past weeks" }).click();
  return samplesWhenStill<{ top: number; list: number }>(page);
}

test("the top edge of the menu sheet stays still while Past weeks opens and closes", async ({ page }) => {
  await page.route((url) => url.hostname !== "127.0.0.1", (route) => route.abort());
  await page.goto(`${server.url}/rankings/`);
  await page.getByRole("button", { name: "Open the menu" }).click();
  const sheet = page.locator("[data-menu-sheet]:not([data-slot='drawer-backdrop'])");
  await expect(sheet).toBeVisible();
  // Wait for the drop of the sheet to end, so the samples hold only the motion of "Past weeks".
  await startSamples(page, readSheet);
  const rest = (await samplesWhenStill<{ top: number; list: number }>(page)).at(-1)!.top;

  for (const step of ["opens", "closes"]) {
    const samples = await togglePast(page);
    const lists = samples.map((sample) => sample.list);
    // The list of weeks moves, so the samples hold the frames of the motion.
    expect(Math.max(...lists) - Math.min(...lists), `the list of weeks grows or shrinks as Past weeks ${step}`).toBeGreaterThan(20);
    const drift = Math.max(...samples.map((sample) => Math.abs(sample.top - rest)));
    expect(drift, `the top edge of the menu sheet moves ${drift}px as Past weeks ${step}`).toBeLessThanOrEqual(1);
  }
});
