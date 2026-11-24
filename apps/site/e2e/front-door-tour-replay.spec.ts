/**
 * The replay of the Tour on the static export in out/ of the current CLIENT, in Chromium: the "Show the tour" row of the
 * menu sheet, the "?" button on desktop, the focus after Done, and no replay control on the other pages.
 */
import { type Page, expect, test } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { TOUR_SEEN_KEY } from "../src/app/front-door/tour-store";
import { serveDir } from "./serve";
import { skipTour } from "./tour";

const OUT = join(process.cwd(), "out");
// The client build writes the hidden /ask/ route only while the flag front_door is off. Then / is the home page.
const DOOR = existsSync(join(OUT, "ask", "index.html")) ? "/ask/" : "/";
const BO_GIRDS = "6";

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

/* A browser with Your team and a kept passphrase. Each call off the test server fails, because the run uses no real API. */
async function setUp(page: Page, width: number, height = 900) {
  await page.route(
    (url) => url.hostname !== "127.0.0.1",
    (route) => route.abort(),
  );
  await page.addInitScript((team) => {
    localStorage.setItem("cpc.passphrase", "test");
    localStorage.setItem("cpc.your-team", team);
    // A kept team lets The Race Announcement open first and cover the page, so the setup marks it seen.
    localStorage.setItem("cpc.announcement.the-race-2026", "seen");
  }, BO_GIRDS);
  await page.setViewportSize({ width, height });
}

/* The front door to a browser that already saw the Tour, so only a replay shows it. */
async function openSeen(page: Page, width: number, height = 900) {
  await skipTour(page);
  await setUp(page, width, height);
  await page.goto(`${server.url}${DOOR}`);
  await expect(page.getByRole("group", { name: "Suggestions" })).toBeVisible();
}

const card = (page: Page, name: string) => page.getByRole("dialog", { name });
const tourButton = (page: Page) =>
  page.getByRole("banner").getByRole("button", { name: "Show the tour" });
const seenKey = (page: Page) => page.evaluate((key) => localStorage.getItem(key), TOUR_SEEN_KEY);

for (const width of [375, 768]) {
  test(`at ${width} px "Show the tour" in the menu sheet closes the sheet, then shows Stop 1 (AT-27)`, async ({
    page,
  }) => {
    await openSeen(page, width);
    await expect(tourButton(page)).toBeHidden();
    await page.getByRole("button", { name: "Open the menu" }).click();
    const sheet = page
      .getByRole("dialog")
      .filter({ has: page.getByRole("navigation", { name: "Pages" }) });
    await expect(sheet).toBeVisible();
    await sheet.getByRole("button", { name: "Show the tour" }).click();
    const stop = card(page, "Suggestions");
    await expect(stop).toBeVisible();
    await expect(stop.getByText("1 of 4")).toBeVisible();
    await expect(page.getByRole("navigation", { name: "Pages" })).toHaveCount(0);
  });
}

test("at 390x660 a replay from the menu sheet waits for the sheet to leave, and blurs a focused ask box before Stop 1 (AT-32)", async ({
  page,
}) => {
  await openSeen(page, 390, 660);
  // The page at the moment the Stop card joins it, before the card moves the focus into itself.
  await page.evaluate(() => {
    const observer = new MutationObserver(() => {
      if (!document.querySelector("[data-tour-card]")) return;
      observer.disconnect();
      const focus = document.activeElement;
      (window as { atCard?: object }).atCard = {
        field: !!focus && focus.matches("input, textarea, [contenteditable]"),
        sheet: document.querySelector('nav[aria-label="Pages"]') !== null,
      };
    });
    observer.observe(document.body, { subtree: true, childList: true });
  });
  await page.getByRole("button", { name: "Open the menu" }).click();
  const sheet = page
    .getByRole("dialog")
    .filter({ has: page.getByRole("navigation", { name: "Pages" }) });
  await sheet.getByRole("button", { name: "Show the tour" }).click();
  // Once the sheet leaves, the reader taps the ask box before Stop 1 shows.
  await expect(page.getByRole("navigation", { name: "Pages" })).toHaveCount(0);
  const field = page.getByRole("textbox", { name: "Ask a question" });
  await field.focus();
  await expect(card(page, "Suggestions")).toBeVisible();
  const atCard = await page.evaluate(() => (window as { atCard?: object }).atCard);
  console.log(`AT-32 page when the Stop card joins it: ${JSON.stringify(atCard)}`);
  expect(atCard).toEqual({ field: false, sheet: false });
  const focus = await page.evaluate(() => {
    const active = document.activeElement as HTMLElement | null;
    return `${active?.tagName} "${(active?.textContent ?? "").trim()}"`;
  });
  console.log(`AT-32 focused element at Stop 1: ${focus}`);
  const focusedField = await page.evaluate(
    () => !!document.activeElement?.matches("input, textarea, [contenteditable]"),
  );
  expect(focusedField).toBe(false);
});

test('at 1280 px the "?" button beside the theme button shows Stop 1, and its name is "Show the tour" (AT-28)', async ({
  page,
}) => {
  await openSeen(page, 1280, 800);
  const replay = tourButton(page);
  await expect(replay).toBeVisible();
  await expect(replay).toHaveAccessibleName("Show the tour");
  // The "?" sits right before the theme button.
  const next = await replay.evaluate((el) => el.nextElementSibling?.getAttribute("aria-label"));
  expect(next).toMatch(/^Switch to (light|dark) theme$/);
  await replay.click();
  const stop = card(page, "Suggestions");
  await expect(stop).toBeVisible();
  await expect(stop.getByText("1 of 4")).toBeVisible();
});

test('after a keyboard replay from the "?" button, Done puts focus back on the "?" button (AT-31)', async ({
  page,
}) => {
  await openSeen(page, 1280, 800);
  await tourButton(page).focus();
  await page.keyboard.press("Enter");
  for (const header of ["Suggestions", "Ask", "Your team"]) {
    await card(page, header).getByRole("button", { name: "Next" }).click();
  }
  await card(page, "Menu").getByRole("button", { name: "Done" }).click();
  await expect(card(page, "Menu")).toHaveCount(0);
  const focus = await page.evaluate(() => {
    const active = document.activeElement as HTMLElement | null;
    return `${active?.tagName} aria-label="${active?.getAttribute("aria-label")}"`;
  });
  console.log(`AT-31 focused element after Done: ${focus}`);
  await expect(tourButton(page)).toBeFocused();
});

for (const path of ["/analyze/", "/2026/week-10/"]) {
  test(`${path} shows no Tour and no replay control, and sets no seen key (AT-34)`, async ({
    page,
  }) => {
    await setUp(page, 375);
    await page.goto(`${server.url}${path}`);
    await page.getByRole("button", { name: "Open the menu" }).click();
    await expect(page.getByRole("navigation", { name: "Pages" })).toBeVisible();
    // The Tour of the front door starts 600 ms after load, so a wait past it shows that no Tour starts here.
    await page.waitForTimeout(1200);
    await expect(page.getByRole("button", { name: "Show the tour" })).toHaveCount(0);
    await expect(page.locator("[data-tour-hole], [data-tour-card]")).toHaveCount(0);
    expect(await seenKey(page)).toBeNull();
  });
}
