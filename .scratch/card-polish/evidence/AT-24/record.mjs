/**
 * Records the roll of the row names of the Index list at 375 px, light theme, motion on: a tap on The Blue Tent, then on Lil Fridge.
 * Run it with the cpc export served on http://127.0.0.1:4173: pnpm --dir apps/site exec node <this file> <out dir>. It prints the time of each tap.
 */
import { createRequire } from "node:module";
import { join } from "node:path";

const outDir = process.argv[2];
// The script sits in the tracker, so it loads Playwright from the site package.
const require = createRequire(join(process.cwd(), "package.json"));
const { chromium } = require("@playwright/test");

const browser = await chromium.launch();
const started = Date.now();
const context = await browser.newContext({
  viewport: { width: 375, height: 812 },
  reducedMotion: "no-preference",
  recordVideo: { dir: outDir, size: { width: 375, height: 812 } },
});
await context.addInitScript(() => localStorage.setItem("cpc.theme", "light"));
const page = await context.newPage();
await page.goto("http://127.0.0.1:4173/2026/managers/");
await page.waitForLoadState("networkidle");
await page.waitForTimeout(1500);
const tap = async (id, name) => {
  await page.locator(`button[aria-controls="index-row-${id}"]`).click();
  console.log(`tap ${name}: ${((Date.now() - started) / 1000).toFixed(2)} s after the context opened`);
};
await tap(1, "The Blue Tent");
await page.waitForTimeout(1500);
await tap(3, "Lil Fridge");
await page.waitForTimeout(1500);
const open = await page.locator('ul[aria-label="Index List"] button[aria-expanded="true"]').allInnerTexts();
console.log(`open rows at the end: ${JSON.stringify(open.map((text) => text.replace(/\s+/g, " ").trim()))}`);
await context.close();
console.log(`video: ${await page.video().path()}`);
await browser.close();
