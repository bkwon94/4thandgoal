/**
 * The scroll of a scrolled-up Thread of the front door at 375 px, in WebKit, on the static export in out/ of the current
 * CLIENT, with motion on. A question sent by a Suggestion chip or the ask box scrolls to its top under the Thread header.
 */
import { type Page, expect, test } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { askQuestion, openDoor, openTopic, samplesWhenStill, startSamples } from "./door-motion";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
// The client build writes the hidden /ask/ route only while the flag front_door is off. Then / is the home page.
const DOOR = existsSync(join(OUT, "ask", "index.html")) ? "/ask/" : "/";

// The browser of a file is set at its top, because a group cannot pick the browser. Safari runs on WebKit.
test.use({ browserName: "webkit", viewport: { width: 375, height: 812 }, reducedMotion: "no-preference" });

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

/* Fill the Thread with three turns, then scroll the page to its top, as a manager does to reread an older Answer. */
async function scrollUp(page: Page) {
  await openTopic(page, "Week recap");
  await openTopic(page, "Power rankings");
  await openTopic(page, "Your season");
  await expect(page.getByRole("list", { name: "All Topics" })).toHaveCount(0);
  await startSamples(page, () => window.scrollY);
  await samplesWhenStill(page);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  await samplesWhenStill(page);
  expect(await page.evaluate(() => window.scrollY), "the page sits at its top").toBe(0);
}

/* Read the gap in px from the bottom of the Thread header to the top of the bubble of the newest question `name`. */
async function gapUnderHeader(page: Page, name: string): Promise<number> {
  const header = (await page.locator('header[aria-label="Thread header"]').boundingBox())!;
  const bubble = (await page.getByRole("article", { name }).last().locator("p").first().boundingBox())!;
  return bubble.y - (header.y + header.height);
}

/* Wait for the smooth scroll to end with the bubble of `name` right under the Thread header. The scroll of WebKit can
   start some frames after the question lands, so the check reads the gap again until it holds or 5 s pass. */
async function expectUnderHeader(page: Page, name: string) {
  await expect.poll(() => gapUnderHeader(page, name), { message: `the bubble top of ${name} sits under the header`, timeout: 5000 }).toBeLessThanOrEqual(16);
  await samplesWhenStill(page);
  const gap = await gapUnderHeader(page, name);
  expect(gap, `the bubble top of ${name} sits ${gap}px under the header`).toBeGreaterThanOrEqual(0);
  expect(gap, `the bubble top of ${name} sits ${gap}px under the header`).toBeLessThanOrEqual(16);
}

test("a Suggestion chip tapped in a scrolled-up Thread scrolls its question to the top under the Thread header", async ({ page }) => {
  // The Suggestions follow the day, so a fixed Friday keeps the same chips on each run. The timers still run.
  await page.clock.setFixedTime(new Date("2026-11-13T12:00:00"));
  await openDoor(page, `${server.url}${DOOR}`);
  await scrollUp(page);
  // The first chip after "More" is a Suggestion. The first tap shows its fact, and the second tap opens it (decision 02).
  const chip = page.getByRole("group", { name: "Suggestions" }).getByRole("button").nth(1);
  const name = (await chip.getAttribute("aria-label"))!.split(":")[0];
  await chip.click();
  await chip.click();
  await expect(page.getByRole("article", { name }).last()).toBeVisible();
  await expectUnderHeader(page, name);
});

test("a question typed in a scrolled-up Thread scrolls to the top under the Thread header", async ({ page }) => {
  await openDoor(page, `${server.url}${DOOR}`);
  await scrollUp(page);
  await askQuestion(page, "week 1 results");
  await expect(page.getByRole("article", { name: "week 1 results" })).toBeVisible();
  await expectUnderHeader(page, "week 1 results");
});
