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

// AT-2: drag down 30 px, let go, sample the bottom edge on each animation frame from the release to rest.
for (const width of [390, 375]) {
const { context, page, cdp } = await phone({}, { width });
await open(page, cdp);
const rest = await box(page, sheetSel);
log(`sheet at rest: ${JSON.stringify(rest)}`);
const before = await page.evaluate((s) => { const cs = getComputedStyle(document.querySelector(s)); return { transition: cs.transition, transitionProperty: cs.transitionProperty, transitionDuration: cs.transitionDuration }; }, sheetSel);
log(`computed transition of the sheet content at rest: ${JSON.stringify(before)}`);
const x = rest.x + rest.width / 2, y = rest.bottom - 20;
await drag(cdp, x, y, y + 30, 200, { release: false });
await wait(150);
const held = await box(page, sheetSel);
log(`bottom during the hold before release: ${held.bottom} (rest ${rest.bottom})`);
const sampler = page.evaluate(async (s) => {
  const out = [];
  await new Promise((r) => requestAnimationFrame(r));
  const t0 = performance.now();
  while (performance.now() - t0 < 900) {
    await new Promise((r) => requestAnimationFrame(r));
    const c = document.querySelector(s);
    const r = c.getBoundingClientRect();
    const cs = getComputedStyle(c);
    out.push({ t: Math.round(performance.now() - t0), bottom: Math.round(r.bottom * 100) / 100, translate: cs.translate, transition: `${cs.transitionProperty} ${cs.transitionDuration}` });
  }
  return out;
}, sheetSel);
await wait(5);
await touch(cdp, "touchEnd");
const frames = await sampler;
log(`frames from the release (transition = computed transition-property and transition-duration) (t=0 is the first frame after the sampler starts, the touchEnd follows within a few ms):`);
let prev = null;
for (const f of frames) {
  log(`  t=${String(f.t).padStart(3)} ms bottom=${f.bottom} offset=${r1(f.bottom - rest.bottom)} step=${prev === null ? "-" : r1(f.bottom - prev)} translate=${f.translate} transition=${f.transition}`);
  prev = f.bottom;
}
const moving = frames.findIndex((f) => Math.abs(f.bottom - held.bottom) > 0.5);
const restIdx = frames.findIndex((f, i) => i >= moving && frames.slice(i).every((g) => Math.abs(g.bottom - rest.bottom) <= 0.5));
log(`first frame that moved: t=${frames[moving]?.t} ms; first frame within 0.5 px of rest for good: t=${frames[restIdx]?.t} ms; time from first move to rest: ${frames[restIdx]?.t - frames[moving]?.t} ms`);
const transitions = [...new Set(frames.map((f) => f.transition))];
log(`distinct computed transition values of the sheet content over the frames: ${JSON.stringify(transitions)}`);
if (width === 375) await page.screenshot({ path: `${HERE}/rest-375.png` });
await context.close();
}
await browser.close();
