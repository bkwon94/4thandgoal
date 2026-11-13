/**
 * The passphrase box of the front door on the static export in out/ of the current CLIENT, in WebKit at the size of an
 * iPhone. It checks that the box comes back above the foot when the keyboard opens after the focus, as on iOS (AT-51).
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
   openKeyboard shrinks it and fires its resize, in that order. No passphrase is kept, so a question asks for it. */
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

/* The box of the passphrase and the top of the foot, in px of the page, read once the scroll comes to rest. */
async function boxAndFoot(page: Page) {
  // The newest card holds the focused box.
  const field = page.getByRole("textbox", { name: "League passphrase" }).last();
  const form = page.getByRole("form", { name: "League passphrase" }).last();
  const foot = page.getByRole("textbox", { name: "Ask a question" }).locator("xpath=ancestor::*[contains(@class,'sticky')][1]");
  let last = "";
  for (;;) {
    await page.waitForTimeout(150);
    const read = JSON.stringify(
      await page.evaluate(
        ([formEl, footEl]) => {
          const box = formEl!.getBoundingClientRect();
          return { top: Math.round(box.top), bottom: Math.round(box.bottom), foot: Math.round(footEl!.getBoundingClientRect().top) };
        },
        [await form.elementHandle(), await foot.elementHandle()],
      ),
    );
    if (read === last) break;
    last = read;
  }
  await expect(field).toBeFocused();
  return JSON.parse(last) as { top: number; bottom: number; foot: number };
}

async function askForPassphrase(page: Page, question: string) {
  const field = page.getByRole("textbox", { name: "Ask a question" });
  await field.tap();
  await field.fill(question);
  await page.getByRole("button", { name: "Send" }).tap();
  // The card takes the focus by itself, before the keyboard of the fake rises.
  await expect(page.getByRole("textbox", { name: "League passphrase" }).last()).toBeFocused();
}

test.describe("the passphrase box with the iOS keyboard (AT-51)", () => {
  /* The second card sits low in the view, where the foot covers it once the keyboard lifts the foot. With the strip, the
     first tap on a chip shows its fact, so the foot is one strip taller. */
  for (const strip of [false, true]) {
    test(`the box comes back above the foot when the keyboard opens after the focus${strip ? ", with the fact strip open" : ""}`, async ({ page }) => {
      await fakeViewport(page);
      await page.goto(`${server.url}${DOOR}`);
      await page.getByRole("dialog").getByRole("button").first().tap();
      await askForPassphrase(page, "Who should I start?");
      if (strip) {
        await page.getByRole("group", { name: "Suggestions" }).getByRole("button").filter({ hasNotText: /^More$/ }).first().tap();
        await expect(page.getByRole("group", { name: "Suggestions" }).getByRole("button", { expanded: true })).toHaveCount(1);
      }
      await askForPassphrase(page, "Who should I sit?");
      // The reader scrolls back up, so the box sits low, right above the foot. A tap focuses it, and then the keyboard rises.
      const field = page.getByRole("textbox", { name: "League passphrase" }).last();
      await field.blur();
      await page.evaluate(() => scrollTo(0, 0));
      await field.tap();
      await page.evaluate((height) => (window as unknown as { openKeyboard: (height: number) => void }).openKeyboard(height), KEYBOARD);
      const place = await boxAndFoot(page);
      console.log(`the box spans ${place.top} to ${place.bottom} px, and the foot starts at ${place.foot} px (keyboard ${KEYBOARD} px${strip ? ", strip open" : ""})`);
      expect(place.bottom, "the whole box is above the foot").toBeLessThanOrEqual(place.foot);
      expect(place.top, "the box is in view").toBeGreaterThanOrEqual(0);
    });
  }
});
