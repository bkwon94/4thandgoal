/**
 * The layout of the front door at / (or at the hidden /ask/ while the flag front_door is off) on the static export in out/ of the current CLIENT, in Chromium. It checks that
 * the 3 Suggestion chips show whole at each width, with no chip cut off at the edge of the row (AT-4 of front-door).
 * It also checks that one tap on Send sends while the keyboard is open (ticket 34), that Send closes the keyboard, and
 * that each tap on a Suggestion chip acts while the keyboard is open: the first shows its fact, the second opens it (ticket 37).
 */
import { type Page, devices, expect, test } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";
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

for (const width of [375, 768, 1280]) {
  test(`the front door shows its 3 Suggestion chips whole at ${width}px (AT-4 of front-door)`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(`${server.url}${DOOR}`);
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

/* The phone of the run: its viewport and touch. A group cannot pick the browser, so the project keeps its own. */
const { defaultBrowserType: _browser, ...phone } = devices["iPhone 15"];

/* iOS keeps the layout viewport at full height and shrinks the visual viewport by the keyboard while a field has the
   focus. The fake keyboard is 336 px tall, and it closes on blur, as the real one does. A kept passphrase lets a question
   route, so no card of the passphrase takes the focus. The API calls fail, because the run uses no real API. */
async function fakeKeyboard(page: Page) {
  await page.route((url) => url.hostname !== "127.0.0.1", (route) => route.abort());
  await page.addInitScript(() => {
    localStorage.setItem("cpc.passphrase", "test");
    const keyboard = () => (document.activeElement?.tagName === "INPUT" ? 336 : 0);
    const view = {
      get height() {
        return innerHeight - keyboard();
      },
      offsetTop: 0,
      addEventListener() {},
      removeEventListener() {},
    };
    Object.defineProperty(window, "visualViewport", { get: () => view });
  });
}

test.describe("Send on a phone with the keyboard open", () => {
  // A phone runs with motion on. With motion off, the dock mounts again at the foot and drops the focus by itself.
  test.use({ ...phone, reducedMotion: "no-preference" });

  test("one tap on Send sends while the field has the focus (ticket 34)", async ({ page }) => {
    await fakeKeyboard(page);
    await page.goto(`${server.url}${DOOR}`);
    await page.getByRole("dialog").getByRole("button").first().tap();
    const field = page.getByRole("textbox", { name: "Ask a question" });
    const send = page.getByRole("button", { name: "Send" });
    const thread = page.getByRole("region", { name: "Thread" });
    // The first question gives the Thread an entry, so the ask box sticks to the foot, right above the keyboard.
    await field.tap();
    await field.fill("Who should I start?");
    await send.tap();
    await expect(field).toHaveValue("");
    await expect(page.getByRole("button", { name: "Clear" })).toBeVisible();
    // The second question is the case of the bug: the field has the focus, and the ask box sits above the keyboard.
    await field.tap();
    await field.fill("Who should I sit?");
    await expect(field).toBeFocused();
    await send.tap();
    await expect(field, "one tap on Send sends the question").toHaveValue("");
    await expect(thread.getByText("Who should I sit?")).toBeVisible();
    // The keyboard closes once the question goes, so the Answer shows (ticket 37).
    await expect(field, "Send closes the keyboard").not.toBeFocused();
  });

  test("each tap on a Suggestion chip acts while the field has the focus (ticket 37)", async ({ page }) => {
    await fakeKeyboard(page);
    await page.goto(`${server.url}${DOOR}`);
    await page.getByRole("dialog").getByRole("button").first().tap();
    const field = page.getByRole("textbox", { name: "Ask a question" });
    const row = page.getByRole("group", { name: "Suggestions" });
    // The first question gives the Thread an entry, so the dock sticks to the foot and moves when the keyboard closes.
    await field.tap();
    await field.fill("Who should I start?");
    await page.getByRole("button", { name: "Send" }).tap();
    await expect(page.getByRole("button", { name: "Clear" })).toBeVisible();
    const chip = row.getByRole("button").filter({ hasNotText: /^More$/ }).first();
    const name = (await chip.getAttribute("aria-label"))!;
    await field.tap();
    await expect(field).toBeFocused();
    // The first tap shows the fact of the chip in the strip, and the keyboard stays open (decision 02).
    await chip.tap();
    await expect(chip, "one tap on the chip shows its fact").toHaveAttribute("aria-expanded", "true");
    await expect(page.getByRole("button", { name: `Open ${name.split(":")[0]}`, exact: true }), "the strip shows").toBeVisible();
    await expect(field, "the first tap keeps the keyboard").toBeFocused();
    // The second tap opens the Topic. A picked Topic drops off the Suggestions, so the chip is gone when the tap acted.
    await chip.tap();
    await expect(row.getByRole("button", { name }), "the second tap on the chip picks it").toHaveCount(0);
    await expect(field, "a chip closes the keyboard").not.toBeFocused();
  });
});
