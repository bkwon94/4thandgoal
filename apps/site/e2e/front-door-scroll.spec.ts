/**
 * The scroll of the Thread of the front door at 375 px, on the static export in out/ of the current CLIENT, with motion
 * on. A new question and a miss scroll to their top under the Thread header, and a short Thread does not jump (tickets 45, 50).
 */
import { type Page, expect, test } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { askQuestion, openDoor, openTopic, samplesWhenStill, startSamples } from "./door-motion";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
// The client build writes the hidden /ask/ route only while the flag front_door is off. Then / is the home page.
const DOOR = existsSync(join(OUT, "ask", "index.html")) ? "/ask/" : "/";

const CORS = { "access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "POST" };

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

test.use({ viewport: { width: 375, height: 812 }, reducedMotion: "no-preference" });

test("a new question scrolls to its top under the Thread header (ticket 45)", async ({ page }) => {
  await openDoor(page, `${server.url}${DOOR}`);
  await openTopic(page, "Week recap");
  await openTopic(page, "Power rankings");
  await startSamples(page, () => window.scrollY);
  await askQuestion(page, "week 1 results");
  const question = page.getByRole("article", { name: "week 1 results" });
  await expect(question).toBeVisible();
  await samplesWhenStill(page);
  const header = (await page.locator('header[aria-label="Thread header"]').boundingBox())!;
  const bubble = (await question.locator("p").first().boundingBox())!;
  const gap = bubble.y - (header.y + header.height);
  expect(gap, `the bubble top sits ${gap}px under the header`).toBeGreaterThanOrEqual(0);
  expect(gap, `the bubble top sits ${gap}px under the header`).toBeLessThanOrEqual(16);
});

/* Read the gap in px from the bottom of the Thread header to the top of the bubble of `name`. */
async function gapUnderHeader(page: Page, name: string): Promise<number> {
  const header = (await page.locator('header[aria-label="Thread header"]').boundingBox())!;
  const bubble = (await page.getByRole("article", { name }).locator("p").first().boundingBox())!;
  return bubble.y - (header.y + header.height);
}

test("a miss scrolls its question to the top, though its dock drops the chips in the same render (ticket 50)", async ({ page }) => {
  await openDoor(page, `${server.url}${DOOR}`);
  // The ask route answers with a miss, so the miss card and the dock without its chips land in one render.
  await page.route("**/clients/*/ask", (route) =>
    route.fulfill({
      status: route.request().method() === "OPTIONS" ? 204 : 200,
      headers: CORS,
      contentType: "application/json",
      body: JSON.stringify({ route: "miss", line: null, topic: null, team: null, closest: ["week_recap", "power_rankings", "playoff_race"], suggestion: null }),
    }),
  );
  await openTopic(page, "Week recap");
  await openTopic(page, "Power rankings");
  // The More panel leaves first, so only the miss changes the height of the dock.
  await expect(page.getByRole("list", { name: "All Topics" })).toHaveCount(0);
  await startSamples(page, () => window.scrollY);
  await askQuestion(page, "who has the best kicker");
  await expect(page.getByRole("article", { name: "who has the best kicker" })).toBeVisible();
  await samplesWhenStill(page);
  const gap = await gapUnderHeader(page, "who has the best kicker");
  expect(gap, `the bubble top sits ${gap}px under the header`).toBeGreaterThanOrEqual(0);
  expect(gap, `the bubble top sits ${gap}px under the header`).toBeLessThanOrEqual(16);
});

test("the first question in a short Thread does not jump the page (ticket 45)", async ({ page }) => {
  await openDoor(page, `${server.url}${DOOR}`);
  await startSamples(page, () => window.scrollY);
  await askQuestion(page, "week 1 results");
  await expect(page.getByRole("article", { name: "week 1 results" })).toBeVisible();
  const scrolls = await samplesWhenStill<number>(page);
  expect(Math.max(...scrolls), "the page never scrolls").toBe(0);
});
