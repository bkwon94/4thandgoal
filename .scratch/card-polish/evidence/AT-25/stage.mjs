/**
 * Shots of the desktop stage of the Index list at 1280 px, motion on: at load, after a hover on The Blue Tent, after a keyboard focus on Lil Fridge.
 * Run it with the cpc export served on http://127.0.0.1:4173: pnpm --dir apps/site exec node <this file> <evidence dir>.
 */
import { createRequire } from "node:module";
import { join } from "node:path";

const outDir = process.argv[2];
// The script sits in the tracker, so it loads Playwright from the site package.
const require = createRequire(join(process.cwd(), "package.json"));
const { chromium } = require("@playwright/test");

const ROW = 'ul[aria-label="Index List"] > li';
const browser = await chromium.launch();
for (const theme of ["light", "dark"]) {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, reducedMotion: "no-preference" });
  await context.addInitScript((value) => localStorage.setItem("cpc.theme", value), theme);
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:4173/2026/managers/");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1500);
  const report = async (state) => {
    const stage = page.locator("[data-ix-stage]");
    const region = await page.getByRole("region", { name: /^Stage: / }).getAttribute("aria-label");
    const slots = await page.locator("[data-ix-stage] [data-hero-slot]").evaluateAll((els) =>
      els.filter((el) => el.getBoundingClientRect().height > 0 && getComputedStyle(el).visibility !== "hidden").map((el) => `${el.getAttribute("data-hero-slot")}: ${el.innerText.replace(/\s+/g, " ").trim()}`));
    const box = await stage.boundingBox();
    const ledger = await page.locator('ul[aria-label="Index List"]').boundingBox();
    const active = await page.evaluate(() => document.activeElement?.closest("li")?.querySelector(".ix-name")?.textContent ?? "none");
    console.log(`${theme} ${state}: region "${region}" | focus on: ${active} | stage x=${Math.round(box.x)} w=${Math.round(box.width)}, ledger x=${Math.round(ledger.x)} w=${Math.round(ledger.width)}, position ${await stage.evaluate((el) => getComputedStyle(el).position)}`);
    for (const slot of slots) console.log(`  ${slot}`);
    await page.screenshot({ path: join(outDir, `${state}-1280-${theme}.png`) });
  };
  await report("load");
  await page.locator(`${ROW}:nth-child(5) button[aria-expanded]`).hover();
  await page.waitForTimeout(1500);
  await report("hover-blue-tent");
  // A keyboard focus: Tab from the row head of The Blue Tent goes to the next row head, Lil Fridge.
  await page.locator(`${ROW}:nth-child(5) button[aria-expanded]`).focus();
  await page.mouse.move(1270, 890);
  await page.keyboard.press("Tab");
  await page.waitForTimeout(1500);
  await report("focus-lil-fridge");
  await context.close();
}
await browser.close();
