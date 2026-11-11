/**
 * The scroll of the Thread of the front door at 375 px, on the static export in out/ of the current CLIENT, with motion
 * on. A new question scrolls to its top under the Thread header, and a short Thread does not jump (ticket 45).
 */
import { expect, test } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { askQuestion, openDoor, openTopic, samplesWhenStill, startSamples } from "./door-motion";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
// The client build writes the hidden /ask/ route only while the flag front_door is off. Then / is the home page.
const DOOR = existsSync(join(OUT, "ask", "index.html")) ? "/ask/" : "/";

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

test("the first question in a short Thread does not jump the page (ticket 45)", async ({ page }) => {
  await openDoor(page, `${server.url}${DOOR}`);
  await startSamples(page, () => window.scrollY);
  await askQuestion(page, "week 1 results");
  await expect(page.getByRole("article", { name: "week 1 results" })).toBeVisible();
  const scrolls = await samplesWhenStill<number>(page);
  expect(Math.max(...scrolls), "the page never scrolls").toBe(0);
});
