/**
 * The Tour of the front door on the static export in out/ of the current CLIENT, in Chromium. Bo Girds, roster 6 of cpc,
 * is Your team. It checks Stop 1 on load, the aim of Stop 4, each control of the card, the seen key, and the dead page.
 */
import { type Page, expect, test } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { serveDir } from "./serve";

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

type Rect = { x: number; y: number; width: number; height: number };

/* A browser with Your team and a kept passphrase, and with no seen key. Each call off the test server fails, because the
   run uses no real API. The egg checks that the page tries to send are kept, so a test can count them. */
async function openTour(page: Page, width: number, height = 900) {
  const eggChecks: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/eggs/check")) eggChecks.push(request.url());
  });
  await page.route((url) => url.hostname !== "127.0.0.1", (route) => route.abort());
  await page.addInitScript((team) => {
    localStorage.setItem("cpc.passphrase", "test");
    localStorage.setItem("cpc.your-team", team);
  }, BO_GIRDS);
  await page.setViewportSize({ width, height });
  await page.goto(`${server.url}${DOOR}`);
  return eggChecks;
}

const card = (page: Page, name: string) => page.getByRole("dialog", { name });
const hole = (page: Page) => page.locator("[data-tour-hole]");

async function rectOf(page: Page, selector: string): Promise<Rect> {
  return page.locator(selector).evaluate((el) => {
    const rect = el.getBoundingClientRect();
    return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
  });
}

const center = (rect: Rect) => ({ x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 });
const inside = (point: { x: number; y: number }, rect: Rect) =>
  point.x >= rect.x && point.x <= rect.x + rect.width && point.y >= rect.y && point.y <= rect.y + rect.height;

/* A point on the dim, away from the card and the hole: the first corner of the screen, 4 px in, that is in neither. */
async function dimPoint(page: Page) {
  const size = page.viewportSize()!;
  const holeRect = await rectOf(page, "[data-tour-hole]");
  const cardRect = await rectOf(page, "[data-tour-card]");
  const corners = [
    { x: 4, y: size.height - 4 },
    { x: size.width - 4, y: size.height - 4 },
    { x: 4, y: 4 },
    { x: size.width - 4, y: 4 },
  ];
  return corners.find((point) => !inside(point, holeRect) && !inside(point, cardRect))!;
}

async function nextTo(page: Page, headers: string[]) {
  for (const header of headers) await card(page, header).getByRole("button", { name: "Next" }).click();
}

test("a browser with Your team and no seen key sees Stop 1 on load, as a modal card, and Stop 1 writes the seen key (AT-2, AT-23, AT-29, AT-39)", async ({ page }) => {
  await openTour(page, 390, 660);
  const stop = card(page, "Suggestions");
  await expect(stop).toBeVisible();
  await expect(page.getByRole("dialog", { name: "Which team is yours?" })).toHaveCount(0);
  await expect(stop).toHaveAttribute("aria-modal", "true");
  await expect(stop).toHaveAccessibleDescription("Picks for your team right now. Tap one to open it, or tap More for the full list.");
  await expect(stop).toContainText("1 of 4");
  expect(await page.evaluate(() => localStorage.getItem("cpc.tour-seen"))).toBe("1");
});

for (const [width, target] of [
  [375, 'button[aria-label="Open the menu"]'],
  [768, 'button[aria-label="Open the menu"]'],
  [1280, 'nav[aria-label="Site menu"]'],
] as const) {
  test(`Stop 4 aims at the visible menu at ${width} px (AT-4)`, async ({ page }) => {
    await openTour(page, width);
    await nextTo(page, ["Suggestions", "Ask", "Your team"]);
    await expect(card(page, "Menu")).toBeVisible();
    await expect(page.locator(target)).toHaveAttribute("data-tour-target", "");
    const holeCenter = center(await rectOf(page, "[data-tour-hole]"));
    const targetCenter = center(await rectOf(page, target));
    expect(Math.abs(holeCenter.x - targetCenter.x)).toBeLessThanOrEqual(1);
    expect(Math.abs(holeCenter.y - targetCenter.y)).toBeLessThanOrEqual(1);
  });
}

test("Next goes to Stop 2 on the ask box, a tap on the dim goes on, and a tap on the dim at Stop 4 ends the Tour (AT-7, AT-8)", async ({ page }) => {
  await openTour(page, 390, 660);
  await card(page, "Suggestions").getByRole("button", { name: "Next" }).click();
  await expect(card(page, "Ask")).toContainText("2 of 4");
  await expect(page.locator('form[aria-label="Ask"]')).toHaveAttribute("data-tour-target", "");
  let point = await dimPoint(page);
  await page.mouse.click(point.x, point.y);
  await expect(card(page, "Your team")).toBeVisible();
  await card(page, "Your team").getByRole("button", { name: "Next" }).click();
  await expect(card(page, "Menu")).toBeVisible();
  point = await dimPoint(page);
  await page.mouse.click(point.x, point.y);
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(hole(page)).toHaveCount(0);
});

test("Skip ends the Tour, and the front door responds to taps again (AT-9)", async ({ page }) => {
  await openTour(page, 390, 660);
  await card(page, "Suggestions").getByRole("button", { name: "Next" }).click();
  await card(page, "Ask").getByRole("button", { name: "Skip" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(hole(page)).toHaveCount(0);
  const more = page.getByRole("group", { name: "Suggestions" }).getByRole("button", { name: "More" });
  await more.click();
  await expect(more).toHaveAttribute("aria-expanded", "true");
});

test("the Escape key counts as Skip at 1280 px (AT-10)", async ({ page }) => {
  await openTour(page, 1280, 800);
  await card(page, "Suggestions").getByRole("button", { name: "Next" }).click();
  await expect(card(page, "Ask")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(hole(page)).toHaveCount(0);
});

test("Stop 4 shows Done and no Next, and Done ends the Tour (AT-12)", async ({ page }) => {
  await openTour(page, 390, 660);
  await nextTo(page, ["Suggestions", "Ask", "Your team"]);
  const stop = card(page, "Menu");
  await expect(stop.getByRole("button", { name: "Next" })).toHaveCount(0);
  await stop.getByRole("button", { name: "Done" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(hole(page)).toHaveCount(0);
});

test("a tap on a Topic in the hole opens no Answer and no passphrase sheet, and goes to Stop 2 (AT-13)", async ({ page }) => {
  await openTour(page, 390, 660);
  await expect(card(page, "Suggestions")).toBeVisible();
  const chip = page.getByRole("group", { name: "Suggestions" }).getByRole("button").filter({ hasNotText: /^More$/ }).first();
  const chipCenter = center((await chip.boundingBox())!);
  expect(inside(chipCenter, await rectOf(page, "[data-tour-hole]")), "the Topic sits in the hole").toBe(true);
  const answersBefore = await page.getByRole("article").count();
  await page.mouse.click(chipCenter.x, chipCenter.y);
  await expect(card(page, "Ask")).toBeVisible();
  expect(await page.getByRole("article").count()).toBe(answersBefore);
  await expect(chip).toHaveAttribute("aria-expanded", "false");
  await expect(page.getByRole("dialog", { name: /passphrase/i })).toHaveCount(0);
});

test("a tap on the menu button in the hole at Stop 4 opens no menu sheet (AT-35)", async ({ page }) => {
  await openTour(page, 375);
  await nextTo(page, ["Suggestions", "Ask", "Your team"]);
  await expect(card(page, "Menu")).toBeVisible();
  const menu = center(await rectOf(page, 'button[aria-label="Open the menu"]'));
  await page.mouse.click(menu.x, menu.y);
  await expect(page.getByRole("dialog", { name: "Menu" })).toHaveCount(0);
  await expect(page.getByRole("navigation", { name: "Pages" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Close the menu" })).toHaveCount(0);
});

test("a second visit after Skip shows no Tour (AT-24)", async ({ page }) => {
  await openTour(page, 390, 660);
  await card(page, "Suggestions").getByRole("button", { name: "Skip" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await page.goto(`${server.url}${DOOR}`);
  await expect(page.getByRole("group", { name: "Suggestions" })).toBeVisible();
  // The Tour waits 600 ms for the dock to settle, so the check waits past that.
  await page.waitForTimeout(1200);
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(hole(page)).toHaveCount(0);
});

test("a reload during the Tour does not start it again (AT-25)", async ({ page }) => {
  await openTour(page, 390, 660);
  await card(page, "Suggestions").getByRole("button", { name: "Next" }).click();
  await expect(card(page, "Ask")).toBeVisible();
  await page.reload();
  await expect(page.getByRole("group", { name: "Suggestions" })).toBeVisible();
  await page.waitForTimeout(1200);
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(hole(page)).toHaveCount(0);
});

test("Tab moves only between Skip and Next at Stop 2 at 1280 px (AT-30)", async ({ page }) => {
  await openTour(page, 1280, 800);
  await card(page, "Suggestions").getByRole("button", { name: "Next" }).click();
  const stop = card(page, "Ask");
  await expect(stop).toBeVisible();
  const focused: string[] = [];
  for (let press = 0; press < 4; press += 1) {
    await page.keyboard.press("Tab");
    focused.push(
      await page.evaluate(() => {
        const active = document.activeElement as HTMLElement | null;
        return active?.closest('[role="dialog"]') ? (active.textContent ?? "").trim() : `outside: ${active?.tagName}`;
      }),
    );
  }
  expect(new Set(focused)).toEqual(new Set(["Skip", "Next"]));
});

test("a 2 s hold on the dim and on the card sends no egg check (AT-33)", async ({ page }) => {
  const eggChecks = await openTour(page, 390, 660);
  await expect(card(page, "Suggestions")).toBeVisible();
  const point = await dimPoint(page);
  await page.mouse.move(point.x, point.y);
  await page.mouse.down();
  await page.waitForTimeout(2000);
  await page.mouse.up();
  const line = card(page, "Ask").getByText(/^Type any question/);
  const lineBox = (await line.boundingBox())!;
  await page.mouse.move(lineBox.x + lineBox.width / 2, lineBox.y + lineBox.height / 2);
  await page.mouse.down();
  await page.waitForTimeout(2000);
  await page.mouse.up();
  expect(eggChecks).toEqual([]);
  await expect(page.getByRole("button", { name: "Crack the egg" })).toHaveCount(0);
});
