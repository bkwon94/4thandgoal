/**
 * Records the open of the card of All You Need Is Love vs Unsolicited Dak Picks at 375 px, light theme, motion on.
 * Run it with the cpc export served on http://127.0.0.1:4173: pnpm --dir apps/site exec node <this file> <out dir>.
 */
import { createRequire } from "node:module";
import { join } from "node:path";

const outDir = process.argv[2];
// The script sits in the tracker, so it loads Playwright from the site package.
const require = createRequire(join(process.cwd(), "package.json"));
const { chromium } = require("@playwright/test");

const head = 'button[aria-controls="recap-4"]:not([aria-label])';
const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: 375, height: 812 },
  reducedMotion: "no-preference",
  recordVideo: { dir: outDir, size: { width: 375, height: 812 } },
});
await context.addInitScript(() => localStorage.setItem("cpc.theme", "light"));
const page = await context.newPage();
await page.goto("http://127.0.0.1:4173/2026/week-08/");
await page.waitForLoadState("networkidle");
await page.evaluate((selector) => {
  const top = document.querySelector(selector).getBoundingClientRect().top + window.scrollY - 80;
  window.scrollTo(0, top);
}, head);
await page.waitForTimeout(1200);
await page.locator(head).click();
await page.waitForTimeout(1500);
console.log(`aria-expanded after the tap: ${await page.locator(head).getAttribute("aria-expanded")}`);
await context.close();
console.log(`video: ${await page.video().path()}`);
await browser.close();
