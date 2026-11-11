/**
 * The glide of the ask box of the front door at 375 px, on the static export in out/ of the current CLIENT, with motion
 * on. On the first question the ask box glides from the center to the bottom in one move, and never rises (ticket 46).
 */
import { expect, test } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { askQuestion, openDoor, samplesWhenStill, startSamples } from "./door-motion";
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

test("the ask box glides to the bottom in one move on the first question (ticket 46)", async ({ page }) => {
  await openDoor(page, `${server.url}${DOOR}`);
  const box = page.getByRole("form", { name: "Ask" });
  // The entrance of the empty Thread settles first, so each sample is the move of the send.
  await startSamples(page, () => Math.round(document.querySelector('form[aria-label="Ask"]')!.getBoundingClientRect().top));
  await samplesWhenStill(page);
  await startSamples(page, () => Math.round(document.querySelector('form[aria-label="Ask"]')!.getBoundingClientRect().top));
  await askQuestion(page, "week 1 results");
  const tops = await samplesWhenStill<number>(page);
  const rises = tops.flatMap((top, index) => (index > 0 && top < tops[index - 1] ? [`${tops[index - 1]} to ${top}`] : []));
  expect(rises, `the top of the ask box moves up: ${tops.join(", ")}`).toEqual([]);
  expect(tops.at(-1)!, "the ask box ends lower than it starts").toBeGreaterThan(tops[0]);
  await expect(box).toBeVisible();
});
