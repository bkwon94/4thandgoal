/**
 * Evidence script of one acceptance test of ui-sdk-sheet, on the static cpc build out/ of the Spec branch, served over HTTP.
 * Run: node script.mjs, with BASE set to the served root. It prints each measured value to the log.
 */
import { createRequire } from "node:module";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
const require = createRequire("/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/ui-sdk-sheet/apps/site/package.json");
const { chromium } = require("@playwright/test");

const BASE = process.env.BASE ?? "http://127.0.0.1:59911/";
const HERE = dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch();
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const log = (...a) => console.log(...a);
const r1 = (n) => Math.round(n * 10) / 10;
const sheetSel = '[data-slot="drawer-content"]';
const dimSel = '[data-slot="drawer-backdrop"]';
const btnSel = 'header button[aria-label$="the menu"]';

/* The phone: 390 x 844 with touch. The front door first shows the team sheet, so the script picks the first team. */
async function phone(opts = {}, { pick = true, width = 390 } = {}) {
  const context = await browser.newContext({ viewport: { width, height: 844 }, hasTouch: true, isMobile: true, ...opts });
  const page = await context.newPage();
  const cdp = await context.newCDPSession(page);
  await page.goto(BASE, { waitUntil: "networkidle" });
  if (pick) {
    await page.locator("text=Which team is yours?").waitFor();
    await page.locator("[role=dialog] button[aria-pressed]").first().click();
    await page.locator("text=Which team is yours?").waitFor({ state: "detached" });
    await wait(1200);
  }
  log(`phone ${width}x844 hasTouch isMobile ${JSON.stringify(opts)} at ${page.url()}`);
  return { context, page, cdp };
}

/* Each touch event carries a monotonic timestamp in seconds, so the CDP round trips do not stretch the gesture. */
let stamp = null;
async function touch(cdp, type, x, y) {
  await cdp.send("Input.dispatchTouchEvent", { type, touchPoints: type === "touchEnd" ? [] : [{ x, y }], ...(stamp === null ? {} : { timestamp: stamp }) });
}
async function drag(cdp, x, y0, y1, ms, { release = true } = {}) {
  const base = Date.now() / 1000;
  stamp = base;
  await touch(cdp, "touchStart", x, y0);
  const steps = Math.max(3, Math.round(ms / 16));
  for (let i = 1; i <= steps; i++) {
    stamp = base + (ms * i) / steps / 1000;
    await touch(cdp, "touchMove", x, y0 + ((y1 - y0) * i) / steps);
  }
  log(`gesture: touchStart (${r1(x)}, ${r1(y0)}), ${steps} touchMove to (${r1(x)}, ${r1(y1)}) over ${ms} ms (event timestamps), ${release ? "touchEnd" : "held"}`);
  if (release) {
    stamp = base + ms / 1000 + 0.001;
    await touch(cdp, "touchEnd");
  }
  stamp = null;
}
async function tap(cdp, x, y) {
  await touch(cdp, "touchStart", x, y);
  await touch(cdp, "touchEnd");
}
const box = async (page, sel) => {
  const b = await page.locator(sel).first().boundingBox();
  return b && { x: r1(b.x), y: r1(b.y), width: r1(b.width), height: r1(b.height), bottom: r1(b.y + b.height) };
};
const expanded = (page) => page.locator(btnSel).getAttribute("aria-expanded");
/* Opens the sheet with a tap on the menu button, then waits for the spring to rest. */
async function open(page, cdp) {
  const b = await page.locator(btnSel).boundingBox();
  await tap(cdp, b.x + b.width / 2, b.y + b.height / 2);
  await page.waitForSelector(sheetSel);
  await wait(900);
  log(`opened: menu button aria-expanded=${await expanded(page)}`);
}

// AT-16: the icon, the name, and the note of each row of the open sheet.
const { context, page, cdp } = await phone();
await open(page, cdp);
const rows = await page.locator(`${sheetSel} nav > ul > li > a`).evaluateAll((as) => as.map((a) => {
  const spans = a.querySelectorAll(":scope > span:nth-of-type(2) > span");
  return { icon: a.querySelector(":scope > span svg")?.getAttribute("class").split(" ").find((c) => c.startsWith("lucide-") && c !== "lucide-icon"), name: spans[0]?.textContent, note: spans[1]?.textContent };
}));
for (const r of rows) log(`row: icon ${r.icon}, name "${r.name}", note "${r.note}"`);
await context.close();
await browser.close();
