/**
 * The shared parts of the site evidence of playoff-paths, round b: the four sizes in Playwright WebKit, the two themes,
 * the local storage of each context, the network log, the full-page shot after a scroll pass, and the overlap check.
 */
import { webkit } from "/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/bbcae1c9-0e99-49c1-be38-1aefbd218ea6/scratchpad/site-b/apps/site/node_modules/@playwright/test/index.mjs";
import { writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

export const EV = "/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/playoff-paths/.scratch/playoff-paths/evidence";
// The cpc export of the Spec head on 4291, and the cpc export with the playoff fixture as the newest week sim on 4292.
export const SITE = "http://127.0.0.1:4291";
export const PLAYOFFS = "http://127.0.0.1:4292";
export const SIZES = [
  { name: "390x660", width: 390, height: 660, touch: true, mobile: true },
  { name: "810x980", width: 810, height: 980, touch: true, mobile: false },
  { name: "1080x740", width: 1080, height: 740, touch: true, mobile: false },
  { name: "1280x800", width: 1280, height: 800, touch: false, mobile: false },
];
export const THEMES = ["light", "dark"];
// Your team is Bo Girds, roster 6. The Tour and both Announcements are seen, unless a test says otherwise.
export const BASE_STORAGE = {
  "cpc.your-team": "6",
  "cpc.tour-seen": "1",
  "cpc.announcement.the-race-2026": "seen",
  "cpc.announcement.season-sim-2026": "seen",
};

export const browser = await webkit.launch();

/* A fresh context of one size and theme. The init script writes each storage key before each load of the page. */
export async function context(size, theme, storage = BASE_STORAGE) {
  const ctx = await browser.newContext({
    viewport: { width: size.width, height: size.height },
    hasTouch: size.touch,
    isMobile: size.mobile,
    reducedMotion: "no-preference",
  });
  await ctx.addInitScript((keys) => {
    for (const [key, value] of Object.entries(keys)) localStorage.setItem(key, value);
  }, { "cpc.theme": theme, ...storage });
  const net = [];
  const errors = [];
  const start = Date.now();
  const at = () => ((Date.now() - start) / 1000).toFixed(2) + "s";
  const local = (url) => url.startsWith(SITE) || url.startsWith(PLAYOFFS);
  ctx.on("request", (r) => { if (!local(r.url())) net.push({ at: at(), page: r.frame()?.url?.() ?? "", event: "request", method: r.method(), url: r.url() }); });
  ctx.on("response", (r) => { if (!local(r.url())) net.push({ at: at(), event: "response", status: r.status(), url: r.url() }); });
  ctx.on("requestfailed", (r) => { if (!local(r.url())) net.push({ at: at(), event: "failed", error: r.failure()?.errorText, url: r.url() }); });
  ctx.on("page", (p) => {
    p.on("console", (m) => { if (m.type() === "error") errors.push("console: " + m.text()); });
    p.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  });
  return { ctx, net, errors };
}

export const sleeper = (net) => net.filter((e) => e.event === "request" && e.url.includes("api.sleeper.app"));

/* Scrolls down a half screen at a time to the end and back, so each section that reveals on scroll shows. */
export async function scrollPass(page) {
  await page.evaluate(async () => {
    const pause = () => new Promise((done) => setTimeout(done, 60));
    const start = window.scrollY;
    const step = Math.max(window.innerHeight / 2, 100);
    for (let y = 0; y < document.documentElement.scrollHeight; y += step) { window.scrollTo(0, y); await pause(); }
    window.scrollTo(0, document.documentElement.scrollHeight); await pause();
    window.scrollTo(0, start);
  });
  await page.waitForTimeout(1200);
}

export async function shot(page, folder, name) {
  mkdirSync(folder, { recursive: true });
  await scrollPass(page);
  const file = join(folder, name + ".png");
  await page.screenshot({ path: file, fullPage: true });
  return file;
}

/*
 * The overlap check. 1: no text line box overlaps a text line box of another element by more than 2 px each way, with
 * each fixed or sticky part hidden, as e2e/trade-block.spec.ts does, and the same text box rule as findOverlap of
 * e2e/smoke.ts. While a modal layer shows, only the texts inside it count. 2: no fixed or sticky bar covers the center of
 * a text box of the content at the top of the page or at the end of the page, where the reader cannot scroll it free.
 * 3: the page does not scroll sideways.
 */
export async function overlapCheck(page) {
  return page.evaluate(() => {
    const limit = 2;
    const describe = (el) => "<" + el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") + "> \"" + (el.textContent ?? "").trim().replace(/\s+/g, " ").slice(0, 40) + "\"";
    const layers = [...document.querySelectorAll('[aria-modal="true"]')].filter((l) => l.checkVisibility());
    const bars = [...document.querySelectorAll("body *")].filter((el) => ["fixed", "sticky"].includes(getComputedStyle(el).position) && el.checkVisibility());
    const clipOf = (element) => {
      let clip = { top: -Infinity, bottom: Infinity, left: -Infinity, right: Infinity };
      for (let at = element; at && at !== document.documentElement; at = at.parentElement) {
        const style = getComputedStyle(at);
        if (style.overflowX === "visible" && style.overflowY === "visible") continue;
        const box = at.getBoundingClientRect();
        clip = { top: Math.max(clip.top, box.top), bottom: Math.min(clip.bottom, box.bottom), left: Math.max(clip.left, box.left), right: Math.min(clip.right, box.right) };
      }
      return clip;
    };
    const textBoxes = (skipBars) => {
      const boxes = [];
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      for (let node = walker.nextNode(); node; node = walker.nextNode()) {
        const owner = node.parentElement;
        if (!owner || !node.textContent?.trim() || owner.closest("script, style, noscript")) continue;
        if (!owner.checkVisibility({ opacityProperty: true, visibilityProperty: true })) continue;
        if (layers.length > 0 && !layers.some((l) => l.contains(owner))) continue;
        if (skipBars && bars.some((b) => b.contains(owner))) continue;
        const clip = clipOf(owner);
        const lh = parseFloat(getComputedStyle(owner).lineHeight);
        const range = document.createRange();
        range.selectNodeContents(node);
        for (const line of range.getClientRects()) {
          const trim = Number.isNaN(lh) ? 0 : Math.max(0, (line.height - lh) / 2);
          const box = { owner, top: Math.max(line.top + trim, clip.top), bottom: Math.min(line.bottom - trim, clip.bottom), left: Math.max(line.left, clip.left), right: Math.min(line.right, clip.right) };
          if (box.bottom - box.top > limit && box.right - box.left > limit) boxes.push(box);
        }
      }
      return boxes;
    };
    // 1. Text over text, with the bars hidden. A bar that holds a modal layer stays, so the layer texts count.
    const hide = layers.length > 0 ? bars.filter((b) => !layers.some((l) => l.contains(b) || b.contains(l))) : bars;
    const old = hide.map((b) => b.style.visibility);
    hide.forEach((b) => (b.style.visibility = "hidden"));
    const overlaps = [];
    const boxes = textBoxes(false).sort((a, b) => a.top - b.top);
    for (const [i, a] of boxes.entries()) {
      for (const b of boxes.slice(i + 1)) {
        if (b.top >= a.bottom - limit) break;
        if (a.owner === b.owner) continue;
        const across = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const down = Math.min(a.bottom, b.bottom) - b.top;
        if (across > limit && down > limit) overlaps.push(describe(a.owner) + " and " + describe(b.owner));
      }
    }
    hide.forEach((b, i) => (b.style.visibility = old[i]));
    // 2. A bar over content, at the top and at the end of the page.
    const covered = [];
    const saved = window.scrollY;
    for (const where of ["top", "end"]) {
      window.scrollTo(0, where === "top" ? 0 : document.documentElement.scrollHeight);
      if (layers.length > 0) break;
      // At the top only a bar in the upper half counts, and at the end only a bar in the lower half, because the reader can
      // scroll any other covered text free.
      const barBoxes = bars.map((b) => ({ b, r: b.getBoundingClientRect() })).filter(({ r }) => (where === "top" ? r.top + r.height / 2 < innerHeight / 2 : r.top + r.height / 2 >= innerHeight / 2));
      for (const t of textBoxes(true)) {
        const cx = (t.left + t.right) / 2, cy = (t.top + t.bottom) / 2;
        if (cy < 0 || cy > innerHeight) continue;
        for (const { b, r } of barBoxes) {
          if (b.contains(t.owner) || t.owner.contains(b)) continue;
          if (cx > r.left && cx < r.right && cy > r.top && cy < r.bottom && getComputedStyle(b).pointerEvents !== "none") {
            const hit = document.elementFromPoint(cx, cy);
            if (hit && b.contains(hit)) covered.push(where + ": " + describe(b) + " covers " + describe(t.owner));
          }
        }
      }
    }
    window.scrollTo(0, saved);
    const sideways = document.documentElement.scrollWidth > window.innerWidth;
    return { textBoxes: boxes.length, fixedOrSticky: bars.length, modalLayers: layers.length, overlaps: [...new Set(overlaps)], covered: [...new Set(covered)], sideways, scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth };
  });
}

export function line(label, result) {
  const verdictFree = "overlaps " + result.overlaps.length + (result.overlaps.length ? " [" + result.overlaps.join("; ") + "]" : "") +
    ", bar covers content " + result.covered.length + (result.covered.length ? " [" + result.covered.join("; ") + "]" : "") +
    ", sideways scroll " + (result.sideways ? "yes (" + result.scrollWidth + " > " + result.innerWidth + ")" : "no") +
    " (text boxes " + result.textBoxes + ", fixed or sticky parts " + result.fixedOrSticky + ", modal layers " + result.modalLayers + ")";
  return label + ": " + verdictFree;
}

export function save(folder, name, text) {
  mkdirSync(folder, { recursive: true });
  writeFileSync(join(folder, name), text.endsWith("\n") ? text : text + "\n");
}

export const netText = (net) => net.map((e) => [e.at, e.event, e.method ?? e.status ?? e.error ?? "", e.url].join(" ")).join("\n") || "(no request to a host other than the local export)";

/* Counts of each text in the visible text of the page. */
export async function counts(page, texts) {
  return page.evaluate((list) => {
    const body = document.body.innerText;
    return Object.fromEntries(list.map((t) => [t, body.split(t).length - 1]));
  }, texts);
}

/* Waits until the live names cache is in session storage, or for the limit. Gives the time it took, or null. */
export async function waitLive(page, ms = 6000) {
  const start = Date.now();
  while (Date.now() - start < ms) {
    const has = await page.evaluate(() => Object.keys(sessionStorage).some((k) => k.startsWith("live-names:")));
    if (has) return Date.now() - start;
    await page.waitForTimeout(100);
  }
  return null;
}
