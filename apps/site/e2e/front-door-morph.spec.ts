/**
 * The morph of a Suggestion chip into its question on the front door at 375 px, on the static export in out/ of the
 * current CLIENT, with motion on. A personal and a trade Topic morph as a league Topic does (ticket 47).
 */
import { type Page, expect, test } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { samplesWhenStill, startSamples } from "./door-motion";
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

/* The Suggestions route of the API serves a fact for a trade and a personal Topic, both urgent, so both show as chips.
   Each other call of the API stays open, so a tapped Topic holds its question while the test watches the morph. */
async function openDoorWithChips(page: Page) {
  await page.route((url) => url.hostname !== "127.0.0.1", (route) => route.abort());
  await page.route("**/clients/**", () => {});
  await page.route("**/clients/*/suggestions", (route) =>
    route.fulfill({
      status: route.request().method() === "OPTIONS" ? 204 : 200,
      headers: { "access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "POST" },
      contentType: "application/json",
      body: JSON.stringify({ facts: { sell_high: "2 to sell", weak_spots: "RB is thin" }, urgent: ["sell_high", "weak_spots"] }),
    }),
  );
  await page.addInitScript(() => localStorage.setItem("cpc.passphrase", "test"));
  await page.goto(`${server.url}${DOOR}`);
  await page.getByRole("dialog").getByRole("button").first().click();
}

test.use({ viewport: { width: 375, height: 812 }, reducedMotion: "no-preference" });

for (const name of ["Weak spots", "Sell high or buy low"]) {
  test(`a tap on the chip of ${name} morphs it into its question (ticket 47)`, async ({ page }) => {
    await openDoorWithChips(page);
    const chip = page.getByRole("group", { name: "Suggestions" }).getByRole("button", { name: new RegExp(`^${name}:`) });
    await expect(chip).toBeVisible();
    // The entrance of the chips settles first, so the box of the chip is where the tap starts.
    await page.waitForTimeout(800);
    const from = (await chip.boundingBox())!;
    await startSamples(page, () => {
      const bubble = document.querySelector("section[aria-label='Thread'] article > p");
      return bubble ? Math.round(bubble.getBoundingClientRect().top) : null;
    });
    await chip.click();
    const tops = (await samplesWhenStill<number | null>(page)).filter((top): top is number => top !== null);
    const end = tops.at(-1)!;
    // One surface moves: the question starts at the chip and glides to its place. A fade shows it at its place at once.
    // A busy run can drop the first frames, so the test looks for the frame nearest the chip.
    const nearest = Math.min(...tops.map((top) => Math.abs(top - from.y)));
    expect(nearest, `the question starts at the chip (${from.y}px): ${tops.join(", ")}`).toBeLessThanOrEqual(40);
    expect(Math.abs(end - from.y), "the question ends away from the chip").toBeGreaterThan(100);
    // The chip leaves once the morph ends, so the question is the one surface left.
    await expect(chip).toHaveCount(0);
  });
}
