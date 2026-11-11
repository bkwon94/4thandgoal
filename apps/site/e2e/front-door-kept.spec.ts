/**
 * The wait of a personal Topic on the front door at 375 px, on the static export in out/ of the current CLIENT, with
 * motion on. A kept Answer shows whole with no step line first (AT-8), and a fresh Answer still shows its steps (AT-65).
 */
import { type Page, expect, test } from "@playwright/test";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { samplesWhenStill, startSamples } from "./door-motion";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
// The client build writes the hidden /ask/ route only while the flag front_door is off. Then / is the home page.
const DOOR = existsSync(join(OUT, "ask", "index.html")) ? "/ask/" : "/";

/* The stream of a kept Answer that the API recorded, the one that the tests of the personal Topics play. */
const KEPT = readFileSync(join(process.cwd(), "src", "fixtures", "personal-answer", "weak-spots-kept.sse"), "utf8");

/* The time in ms that the API takes to send a kept Answer from its store. The run of AT-8 saw about 200 ms from the tap. */
const STORE_MS = 150;

const CORS = { "access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "POST" };

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

/* The Suggestions route of the API serves Weak spots as an urgent personal Topic, so it shows as a chip. The personal
   route sends the kept Answer after STORE_MS, or with `kept` false it stays open, as a fresh Answer that waits. */
async function openDoorWithWeakSpots(page: Page, { kept }: { kept: boolean }) {
  await page.route((url) => url.hostname !== "127.0.0.1", (route) => route.abort());
  await page.route("**/clients/**", () => {});
  await page.route("**/clients/*/suggestions", (route) =>
    route.fulfill({
      status: route.request().method() === "OPTIONS" ? 204 : 200,
      headers: CORS,
      contentType: "application/json",
      body: JSON.stringify({ facts: { weak_spots: "QB ranks 7th of 12" }, urgent: ["weak_spots"] }),
    }),
  );
  await page.route("**/clients/*/personal", async (route) => {
    if (route.request().method() === "OPTIONS") return route.fulfill({ status: 204, headers: CORS });
    if (!kept) return;
    await new Promise((done) => setTimeout(done, STORE_MS));
    await route.fulfill({
      status: 200,
      headers: { ...CORS, "access-control-expose-headers": "*", "x-vercel-ai-ui-message-stream": "v1" },
      contentType: "text/event-stream",
      body: KEPT,
    });
  });
  await page.addInitScript(() => localStorage.setItem("cpc.passphrase", "test"));
  await page.goto(`${server.url}${DOOR}`);
  await page.getByRole("dialog").getByRole("button").first().click();
}

/* The chip of Weak spots in the row of Suggestions. */
const weakSpotsChip = (page: Page) => page.getByRole("group", { name: "Suggestions" }).getByRole("button", { name: /^Weak spots:/ });

test.use({ viewport: { width: 375, height: 812 }, reducedMotion: "no-preference" });

test("a tap on a personal Topic whose Answer is kept shows no step line on any frame (AT-8, ticket 49)", async ({ page }) => {
  await openDoorWithWeakSpots(page, { kept: true });
  await expect(weakSpotsChip(page)).toBeVisible();
  // Each frame reads the step lines and the text of the Answer in the Thread.
  await startSamples(page, () => {
    const article = document.querySelector("section[aria-label='Thread'] article[aria-label='Weak spots']");
    if (!article) return null;
    const lines = [...article.querySelectorAll("ol[aria-label='Steps'] li")].map((item) => item.textContent ?? "");
    return { lines, checked: (article.textContent ?? "").includes("Checked") };
  });
  await weakSpotsChip(page).click();
  const frames = (await samplesWhenStill<{ lines: string[]; checked: boolean } | null>(page, 30)).filter((frame) => frame !== null);
  expect(frames.at(-1)?.checked, "the kept Answer ends checked").toBe(true);
  const withSteps = frames.filter((frame) => frame.lines.length > 0);
  expect(withSteps, `frames with a step line: ${JSON.stringify(withSteps.slice(0, 3))}`).toEqual([]);
});

test("a fresh Answer of a personal Topic still waits on the live first line with the braille spinner (AT-65)", async ({ page }) => {
  await openDoorWithWeakSpots(page, { kept: false });
  await weakSpotsChip(page).click();
  const step = page.getByRole("article", { name: "Weak spots" }).getByRole("list", { name: "Steps" }).getByRole("listitem").first();
  await expect(step).toHaveText(/Reading the league…/);
  await expect(step).toHaveAttribute("data-state", "live");
  // The live step turns a braille spinner, so its mark shows a braille frame.
  await expect(step.locator("[data-mark]")).toHaveText(/^[⠀-⣿]$/);
});
