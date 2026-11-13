/**
 * The passphrase box of the team sheet of the front door on the static export in out/ of the current CLIENT, in WebKit at
 * the size of an iPhone. It checks that the box sits above the keyboard when the keyboard opens after the focus, as on iOS (AT-51).
 */
import { type Page, devices, expect, test } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
// The client build writes the hidden /ask/ route only while the flag front_door is off. Then / is the home page.
const DOOR = existsSync(join(OUT, "ask", "index.html")) ? "/ask/" : "/";
const KEYBOARD = 336;

// The browser of a file is set at its top, because a group cannot pick the browser. iOS Safari runs on WebKit.
const { defaultBrowserType: _browser, ...phone } = devices["iPhone 15"];
test.use({ ...phone, browserName: "webkit", viewport: { width: 393, height: 852 }, isMobile: false, reducedMotion: "no-preference" });

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

/* iOS keeps the layout viewport at full height and shrinks the visual viewport by the keyboard. On a tap, the field
   takes the focus first, and the keyboard rises after it. The fake visual viewport starts at full height, and
   openKeyboard shrinks it and fires its resize, in that order. No passphrase is kept, so the sheet asks for it. */
async function fakeViewport(page: Page) {
  await page.route((url) => url.hostname !== "127.0.0.1", (route) => route.abort());
  await page.addInitScript(() => {
    localStorage.removeItem("cpc.passphrase");
    let keyboard = 0;
    // Object.assign would copy the value of the getter once, so the height getter goes on with defineProperties.
    const view = Object.defineProperties(new EventTarget(), {
      height: { get: () => innerHeight - keyboard },
      offsetTop: { value: 0 },
    });
    Object.defineProperty(window, "visualViewport", { get: () => view });
    Object.assign(window, {
      openKeyboard: (height: number) => {
        keyboard = height;
        view.dispatchEvent(new Event("resize"));
      },
    });
  });
}

/* The box of the passphrase and the top of the keyboard, in px of the page, read once the sheet comes to rest. */
async function boxAndKeyboard(page: Page) {
  const field = page.getByRole("dialog").getByLabel("League passphrase", { exact: true }).and(page.locator("input"));
  const form = page.getByRole("dialog").getByRole("form", { name: "League passphrase" });
  let last = "";
  for (;;) {
    await page.waitForTimeout(150);
    const read = JSON.stringify(
      await form.evaluate((formEl, keyboard) => {
        const box = formEl.getBoundingClientRect();
        return { top: Math.round(box.top), bottom: Math.round(box.bottom), keyboard: innerHeight - keyboard };
      }, KEYBOARD),
    );
    if (read === last) break;
    last = read;
  }
  await expect(field).toBeFocused();
  return JSON.parse(last) as { top: number; bottom: number; keyboard: number };
}

/* A tap focuses the field first, and then the keyboard rises, as on iOS. */
async function tapAndOpenKeyboard(page: Page) {
  const field = page.getByRole("dialog").getByLabel("League passphrase", { exact: true }).and(page.locator("input"));
  await expect(field).toBeFocused();
  await field.blur();
  await field.tap();
  await page.evaluate((height) => (window as unknown as { openKeyboard: (height: number) => void }).openKeyboard(height), KEYBOARD);
}

test.describe("the passphrase box of the team sheet with the iOS keyboard (AT-51)", () => {
  test("the box sits above the keyboard on the first visit, right after the team", async ({ page }) => {
    await fakeViewport(page);
    await page.goto(`${server.url}${DOOR}`);
    await page.getByRole("dialog").getByRole("button").first().tap();
    await expect(page.getByRole("dialog", { name: "What is the league passphrase?" })).toBeVisible();
    await tapAndOpenKeyboard(page);
    const place = await boxAndKeyboard(page);
    console.log(`the box spans ${place.top} to ${place.bottom} px, and the keyboard starts at ${place.keyboard} px`);
    expect(place.bottom, "the whole box is above the keyboard").toBeLessThanOrEqual(place.keyboard);
    expect(place.top, "the box is in view").toBeGreaterThanOrEqual(0);
  });

  test("the box sits above the keyboard when a question needs the passphrase", async ({ page }) => {
    await fakeViewport(page);
    // A kept team with no kept passphrase, as on a phone that picked the team before the passphrase moved to the sheet.
    await page.addInitScript(() => localStorage.setItem("cpc.your-team", "1"));
    await page.goto(`${server.url}${DOOR}`);
    const ask = page.getByRole("textbox", { name: "Ask a question" });
    await ask.tap();
    await ask.fill("Who should I start?");
    await page.getByRole("button", { name: "Send" }).tap();
    await expect(page.getByRole("dialog", { name: "What is the league passphrase?" })).toBeVisible();
    await expect(page.getByRole("region", { name: "Thread" }).getByRole("form", { name: "League passphrase" }), "the Thread holds no passphrase box").toHaveCount(0);
    await tapAndOpenKeyboard(page);
    const place = await boxAndKeyboard(page);
    expect(place.bottom, "the whole box is above the keyboard").toBeLessThanOrEqual(place.keyboard);
    expect(place.top, "the box is in view").toBeGreaterThanOrEqual(0);
  });
});
