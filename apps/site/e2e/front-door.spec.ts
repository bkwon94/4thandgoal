/**
 * The layout of the front door at / on the static export in out/ of the current CLIENT, in Chromium. It checks that
 * the 3 Suggestion chips show whole at each width, with no chip cut off at the edge of the row (AT-4 of front-door).
 */
import { expect, test } from "@playwright/test";
import { join } from "node:path";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

for (const width of [375, 768, 1280]) {
  test(`the front door shows its 3 Suggestion chips whole at ${width}px (AT-4 of front-door)`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(`${server.url}/`);
    // A first visit asks for Your team. The first team of the sheet works for each client.
    await page.getByRole("dialog").getByRole("button").first().click();
    const row = page.getByRole("group", { name: "Suggestions" });
    await expect(row).toBeVisible();
    const chips = row.getByRole("button").filter({ hasNotText: /^More$/ });
    await expect(chips).toHaveCount(3);
    const edge = await row.evaluate((element) => {
      const box = element.getBoundingClientRect();
      return { left: box.left, right: box.right, scrolls: element.scrollWidth > element.clientWidth };
    });
    // A row that scrolls sideways hides a chip past its edge until a swipe.
    expect(edge.scrolls, "the Suggestions row scrolls sideways").toBe(false);
    for (const chip of await chips.all()) {
      const box = (await chip.boundingBox())!;
      expect(box.x, `${await chip.innerText()} starts inside the row`).toBeGreaterThanOrEqual(Math.max(0, edge.left) - 0.5);
      expect(box.x + box.width, `${await chip.innerText()} ends inside the row`).toBeLessThanOrEqual(Math.min(width, edge.right) + 0.5);
    }
  });
}
