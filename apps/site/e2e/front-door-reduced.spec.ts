/**
 * The front door under reduced motion at 375 px, on the static export in out/ of the current CLIENT. On the first
 * question the ask box and the Answer fade by opacity only, with no glide, no blur, and no spring (ticket 48).
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

test.use({ viewport: { width: 375, height: 812 }, reducedMotion: "reduce" });

test("under reduced motion the ask box fades on the first question, with no jump of its opacity (ticket 48)", async ({ page }) => {
  await openDoor(page, `${server.url}${DOOR}`);
  // The entrance of the empty Thread settles first, so each sample is the change of the send.
  await page.waitForTimeout(800);
  // The ask box as the reader sees it: the opacity of its form times the opacity of each part around it. A cross-fade
  // shows two ask boxes for a moment, so the sample takes the one that shows the most.
  await startSamples(page, () => {
    const seen = [...document.querySelectorAll('form[aria-label="Ask"]')].map((form) => {
      let opacity = 1;
      for (let node: Element | null = form; node; node = node.parentElement) opacity *= Number(getComputedStyle(node).opacity);
      return Math.round(opacity * 100) / 100;
    });
    const filters = [...document.querySelectorAll("section[aria-label='Thread'] *")].filter((node) => !["none", ""].includes(getComputedStyle(node).filter)).length;
    const moves = [...document.querySelectorAll('form[aria-label="Ask"]')].filter((form) => {
      for (let node: Element | null = form; node; node = node.parentElement) if (!["none", ""].includes(getComputedStyle(node).transform)) return true;
      return false;
    }).length;
    return { opacity: Math.max(0, ...seen), filters, moves };
  });
  await askQuestion(page, "week 1 results");
  await expect(page.getByRole("article", { name: "week 1 results" })).toBeVisible();
  const samples = await samplesWhenStill<{ opacity: number; filters: number; moves: number }>(page);
  const opacities = samples.map((sample) => sample.opacity);
  const jumps = opacities.flatMap((opacity, index) => (index > 0 && opacities[index - 1] - opacity > 0.5 ? [`${opacities[index - 1]} to ${opacity}`] : []));
  expect(jumps, `the opacity of the ask box: ${opacities.join(", ")}`).toEqual([]);
  expect(opacities.at(-1), "the ask box shows at the end").toBe(1);
  expect(Math.max(...samples.map((sample) => sample.filters)), "no part of the Thread blurs").toBe(0);
  expect(Math.max(...samples.map((sample) => sample.moves)), "the ask box never glides").toBe(0);
});
