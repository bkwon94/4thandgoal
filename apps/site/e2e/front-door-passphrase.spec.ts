/**
 * The passphrase box of the passphrase modal of the front door on the static export in out/ of the current CLIENT, in
 * WebKit at the size of an iPhone. It checks that the box sits above the keyboard when the keyboard opens after the focus,
 * as on iOS (AT-51).
 */
import { type Page, devices, expect, test } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { SIM_ANNOUNCEMENT } from "../src/app/_routes/sim/announcement";
import { LOAD_BEAT_MS } from "../src/app/use-announcement";
import { skipAnnouncements } from "./announcement";
import { serveDir } from "./serve";
import { skipTour } from "./tour";

/* Each test starts as a league mate who already saw the Tour and each Announcement, so no layer of the load beat covers
   the front door that it checks. */
test.beforeEach(async ({ page }) => {
  await skipTour(page);
  await skipAnnouncements(page);
});

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
   openKeyboard shrinks it and fires its resize, in that order. No passphrase is kept, so the first action asks for it. */
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

/* A loaded runner or a slow phone can draw no frame for a few hundred ms, while each motion still runs. The Drawer lifts
   the sheet over the keyboard with a slide of 250 ms from its old place to "0 0". So the keyboard slide freezes at 60 ms
   for 600 ms, still in its running state, and then plays to its end. The box must still come to rest above the keyboard. */
async function stallKeyboardSlide(page: Page) {
  await page.addInitScript(() => {
    const animate = Element.prototype.animate;
    Element.prototype.animate = function (keyframes, options) {
      const animation = animate.call(this, keyframes, options);
      const to = keyframes && !Array.isArray(keyframes) ? keyframes.translate : undefined;
      if (Array.isArray(to) && to.at(-1) === "0 0") {
        animation.currentTime = 60;
        animation.playbackRate = 0;
        window.setTimeout(() => (animation.playbackRate = 1), 600);
      }
      return animation;
    };
  });
}

/* The box of the passphrase and the top of the keyboard, in px of the page, read once the sheet comes to rest. Two equal
   reads are no proof of rest, because a loaded runner can draw no frame between them while the slide still moves. So the
   read waits for the Drawer to take the keyboard inset, and then for each running motion of the sheet to end. */
async function boxAndKeyboard(page: Page) {
  const field = page.getByRole("dialog").getByLabel("League passphrase", { exact: true }).and(page.locator("input"));
  const form = page.getByRole("dialog").getByRole("form", { name: "League passphrase" });
  // The Drawer writes --keyboard-inset on the host of the sheet, and starts its keyboard slide in the same step.
  const inset = () =>
    form.evaluate((formEl) => {
      let el: HTMLElement | SVGElement | null = formEl;
      while (el && !el.style.getPropertyValue("--keyboard-inset")) el = el.parentElement;
      return el?.style.getPropertyValue("--keyboard-inset") ?? "";
    });
  await expect.poll(inset, { message: "the Drawer lifts the sheet by the keyboard" }).toBe(`${KEYBOARD}px`);
  const place = await form.evaluate(async (formEl, keyboard) => {
    let host: HTMLElement | SVGElement | null = formEl;
    while (host && !host.style.getPropertyValue("--keyboard-inset")) host = host.parentElement;
    /* A motion runs on the clock of the document. The Drawer also keeps paused animations for the dim and the drag, and
       animations on a scroll timeline that follow the scroll of the sheet. Those never end on their own, so they do not
       count. A canceled slide rejects its finished promise, so allSettled waits for each. */
    const moving = (host ?? formEl)
      .getAnimations({ subtree: true })
      .filter((animation) => animation.playState === "running" && animation.timeline === document.timeline);
    await Promise.allSettled(moving.map((animation) => animation.finished));
    const box = formEl.getBoundingClientRect();
    return { top: Math.round(box.top), bottom: Math.round(box.bottom), keyboard: innerHeight - keyboard };
  }, KEYBOARD);
  await expect(field).toBeFocused();
  return place;
}

/* A tap focuses the field first, and then the keyboard rises, as on iOS. */
async function tapAndOpenKeyboard(page: Page) {
  const field = page.getByRole("dialog").getByLabel("League passphrase", { exact: true }).and(page.locator("input"));
  await expect(field).toBeFocused();
  await field.blur();
  await field.tap();
  await page.evaluate((height) => (window as unknown as { openKeyboard: (height: number) => void }).openKeyboard(height), KEYBOARD);
}

/* The page clock starts on the release day of the season sim, so its Announcement can open on each run, whatever the date
   of the run. */
async function startClock(page: Page) {
  await page.clock.install({ time: new Date(`${SIM_ANNOUNCEMENT.release}T12:00:00`) });
}

/* A slow runner reaches the first tap after the load beat, so an Announcement or the Tour can open first. The page clock
   moves past the load beat and the first start of the Tour, so that happens on each run. Then no layer may cover the
   front door. */
async function passLoadBeat(page: Page) {
  await page.clock.fastForward(LOAD_BEAT_MS + 1000);
  await expect(page.getByRole("dialog"), "no Announcement and no Tour covers the front door before the first tap").toHaveText([]);
}

/* Ask a question with no kept passphrase, so the passphrase modal opens, and the Thread holds no passphrase box. */
async function askForPassphrase(page: Page) {
  const ask = page.getByRole("textbox", { name: "Ask a question" });
  await ask.tap();
  await ask.fill("Who should I start?");
  await page.getByRole("button", { name: "Send" }).tap();
  await expect(page.getByRole("dialog", { name: "What is the league passphrase?" })).toBeVisible();
  await expect(page.getByRole("region", { name: "Thread" }).getByRole("form", { name: "League passphrase" }), "the Thread holds no passphrase box").toHaveCount(0);
}

test.describe("the passphrase box of the passphrase modal with the iOS keyboard (AT-51)", () => {
  test("the team sheet asks only for the team, and the box sits above the keyboard on the first Topic tap", async ({ page }) => {
    await fakeViewport(page);
    await stallKeyboardSlide(page);
    await startClock(page);
    await page.goto(`${server.url}${DOOR}`);
    await page.getByRole("dialog").getByRole("button").first().tap();
    await expect(page.getByRole("dialog"), "the pick of the team closes the sheet, and no modal opens on its own").toHaveCount(0);
    await passLoadBeat(page);
    // A weekly Topic from "More" needs no API, and the first action still asks for the passphrase.
    await page.getByRole("group", { name: "Suggestions" }).getByRole("button", { name: "More" }).tap();
    await page.getByRole("list", { name: "All Topics" }).getByRole("button").first().tap();
    await expect(page.getByRole("dialog", { name: "What is the league passphrase?" })).toBeVisible();
    await tapAndOpenKeyboard(page);
    const place = await boxAndKeyboard(page);
    console.log(`the box spans ${place.top} to ${place.bottom} px, and the keyboard starts at ${place.keyboard} px`);
    expect(place.bottom, "the whole box is above the keyboard").toBeLessThanOrEqual(place.keyboard);
    expect(place.top, "the box is in view").toBeGreaterThanOrEqual(0);
  });

  test("the box sits above the keyboard with a kept team and no kept passphrase", async ({ page }) => {
    await fakeViewport(page);
    await stallKeyboardSlide(page);
    await startClock(page);
    // A kept team lets an Announcement open on the load beat.
    await page.addInitScript(() => localStorage.setItem("cpc.your-team", "1"));
    await page.goto(`${server.url}${DOOR}`);
    await page.getByRole("textbox", { name: "Ask a question" }).waitFor();
    await passLoadBeat(page);
    await askForPassphrase(page);
    await tapAndOpenKeyboard(page);
    const place = await boxAndKeyboard(page);
    expect(place.bottom, "the whole box is above the keyboard").toBeLessThanOrEqual(place.keyboard);
    expect(place.top, "the box is in view").toBeGreaterThanOrEqual(0);
  });
});
