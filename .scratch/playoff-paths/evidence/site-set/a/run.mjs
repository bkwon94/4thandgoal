/**
 * The site evidence set of playoff-paths, tests AT-26 to AT-43: Playwright WebKit at 390x660, 810x980, 1080x740, and 1280x800,
 * light and dark, with an overlap check of each shot. Run: node run.mjs <client> <site url> <api url> <AT-n> ...
 */
import { createRequire } from "node:module";
import { appendFileSync, mkdirSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

// Playwright resolves from the site app of the checkout, named by SITE_APP.
const require = createRequire(join(process.env.SITE_APP, "package.json"));
const { webkit, devices } = require("@playwright/test");
const EVIDENCE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const [client, site, api, ...ids] = process.argv.slice(2);

// The four viewports of the site evidence set, each with the WebKit profile of its device.
const VIEWS = [
  { w: 390, h: 660, device: "iPhone 15" },
  { w: 810, h: 980, device: "iPad Pro 11" },
  { w: 1080, h: 740, device: "iPad Pro 11 landscape" },
  { w: 1280, h: 800, device: "Desktop Safari" },
];
const THEMES = ["light", "dark"];
// Your team: Bo Girds is roster 6 in cpc and roster 7 in norcal.
const YOUR_TEAM = { cpc: "6", norcal: "7" };

const pause = (page, ms) => page.waitForTimeout(ms);

/* Scrolls the page to the end and back, so each section that reveals on scroll shows, as the repo runner does. */
async function scrollPass(page) {
  await page.evaluate(async () => {
    const wait = () => new Promise((r) => setTimeout(r, 50));
    const start = window.scrollY;
    const step = Math.max(window.innerHeight / 2, 100);
    for (let y = 0; y < document.documentElement.scrollHeight; y += step) { window.scrollTo(0, y); await wait(); }
    window.scrollTo(0, document.documentElement.scrollHeight); await wait();
    window.scrollTo(0, start);
  });
  await pause(page, 1200);
}

/*
 * The overlap check, run in the page. With an open dialog it checks only the text of the dialog, because the dialog covers the
 * page by design. (a) Each pair of visible text boxes of two text nodes must not overlap by more than 3 px in both directions.
 * (b) At the top and at the end of the page, the center of each text box in the viewport must hit its own text, not a fixed or
 * sticky element of another part.
 */
async function overlapCheck(page) {
  return page.evaluate(async () => {
    const dialogs = [...document.querySelectorAll('[role=dialog],[role=alertdialog]')].filter((d) => d.getBoundingClientRect().height > 0 && d.checkVisibility({ opacityProperty: true, visibilityProperty: true }));
    const root = dialogs.at(-1) ?? document.body;
    const pinned = (el) => { for (let e = el; e && e !== document.documentElement; e = e.parentElement) { const p = getComputedStyle(e).position; if (p === "fixed" || p === "sticky") return e; } return null; };
    const clipBox = (el, r) => {
      let { left, top, right, bottom } = r;
      for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
        const cs = getComputedStyle(e);
        if (cs.overflowX !== "visible" || cs.overflowY !== "visible" || cs.clipPath !== "none" || (cs.clip && cs.clip !== "auto")) {
          const b = e.getBoundingClientRect();
          left = Math.max(left, b.left); top = Math.max(top, b.top); right = Math.min(right, b.right); bottom = Math.min(bottom, b.bottom);
        }
      }
      return right - left > 1 && bottom - top > 1 ? { left, top, right, bottom } : null;
    };
    const collect = () => {
      const out = [];
      const walk = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      let n, i = 0;
      while ((n = walk.nextNode())) {
        const text = n.textContent.replace(/\s+/g, " ").trim();
        if (!text) continue;
        const el = n.parentElement;
        if (!el.checkVisibility({ opacityProperty: true, visibilityProperty: true })) continue;
        const range = document.createRange(); range.selectNodeContents(n);
        const pin = pinned(el);
        for (const r of range.getClientRects()) {
          if (r.width < 1 || r.height < 1) continue;
          const c = clipBox(el, r);
          if (!c) continue;
          out.push({ node: i, el, text: text.slice(0, 50), pin, ...c });
        }
        i++;
      }
      return out;
    };
    const boxes = collect();
    const overlaps = [];
    for (let a = 0; a < boxes.length; a++) for (let b = a + 1; b < boxes.length; b++) {
      const p = boxes[a], q = boxes[b];
      if (p.node === q.node) continue;
      // Boxes of a fixed or sticky part move with the viewport, so they compare only with each other.
      if (!!p.pin !== !!q.pin) continue;
      const w = Math.min(p.right, q.right) - Math.max(p.left, q.left);
      const h = Math.min(p.bottom, q.bottom) - Math.max(p.top, q.top);
      if (w > 3 && h > 3 && h > 0.25 * Math.min(p.bottom - p.top, q.bottom - q.top))
        overlaps.push(`"${p.text}" overlaps "${q.text}" by ${w.toFixed(0)}x${h.toFixed(0)} px`);
    }
    // At the end of the page, content scrolls under a top bar by design, so only a bar in the lower half of the viewport counts there.
    const covered = async (where) => {
      const out = [];
      for (const b of collect()) {
        if (b.pin) continue;
        const x = (b.left + b.right) / 2, y = (b.top + b.bottom) / 2;
        if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) continue;
        const hit = document.elementFromPoint(x, y);
        if (!hit || hit === b.el || b.el.contains(hit) || hit.contains(b.el)) continue;
        const pin = pinned(hit);
        if (pin && where.endsWith("end") && pin.getBoundingClientRect().top < innerHeight / 2) continue;
        // At the top of the page, content starts under a bottom bar and scrolls out from under it, so only a bar in the upper half counts there.
        if (pin && where === "top" && pin.getBoundingClientRect().bottom > innerHeight / 2) continue;
        if (pin && !pin.contains(b.el)) out.push(`${where}: "${b.text}" sits under a ${getComputedStyle(pin).position} <${pin.tagName.toLowerCase()}${pin.getAttribute("aria-label") ? " " + pin.getAttribute("aria-label") : ""}>`);
      }
      return out;
    };
    const start = scrollY;
    const scroller = root === document.body ? null : [...root.querySelectorAll("*")].find((e) => e.scrollHeight > e.clientHeight + 4 && /auto|scroll/.test(getComputedStyle(e).overflowY));
    const settle = () => new Promise((r) => setTimeout(r, 400));
    let cov = [];
    if (root === document.body) {
      window.scrollTo(0, 0); await settle(); cov = cov.concat(await covered("top"));
      window.scrollTo(0, document.documentElement.scrollHeight); await settle(); cov = cov.concat(await covered("end"));
      window.scrollTo(0, start); await settle();
    } else {
      cov = cov.concat(await covered("sheet top"));
      if (scroller) { const s0 = scroller.scrollTop; scroller.scrollTop = scroller.scrollHeight; await settle(); cov = cov.concat(await covered("sheet end")); scroller.scrollTop = s0; await settle(); }
    }
    return { scope: root === document.body ? "page" : "open dialog", boxes: boxes.length, overlaps, covered: cov };
  });
}


/*
 * The check of a viewport shot, run in the page at the scroll of the shot. It checks every visible text box in the viewport.
 * (a) Two text boxes of two text nodes must not overlap by more than 3 px both ways, where both show.
 * (b) Each text box of the page under a fixed or sticky bar is either hidden by an opaque layer of the bar (alpha 1 and
 * opacity 1) or shows through the bar. A box that shows through is listed.
 */
async function viewCheck(page) {
  return page.evaluate(() => {
    const dialogs = [...document.querySelectorAll('[role=dialog],[role=alertdialog]')].filter((d) => d.getBoundingClientRect().height > 0 && d.checkVisibility({ opacityProperty: true, visibilityProperty: true }));
    const root = dialogs.at(-1) ?? document.body;
    const pinned = (el) => { for (let e = el; e && e !== document.documentElement; e = e.parentElement) { const p = getComputedStyle(e).position; if (p === "fixed" || p === "sticky") return e; } return null; };
    const alpha = (css) => { const m = css.match(/rgba?\(([^)]+)\)/); if (m) { const v = m[1].split(/[ ,\/]+/).filter(Boolean); return v.length > 3 ? Number(v[3]) : 1; } const n = css.match(/\/\s*([\d.]+)\s*\)/); if (n) return Number(n[1]); return css === "transparent" ? 0 : 1; };
    const opacityChain = (el) => { let o = 1; for (let e = el; e; e = e.parentElement) o *= Number(getComputedStyle(e).opacity); return o; };
    const clipBox = (el, r) => {
      let { left, top, right, bottom } = r;
      for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
        const cs = getComputedStyle(e);
        if (cs.overflowX !== "visible" || cs.overflowY !== "visible" || cs.clipPath !== "none" || (cs.clip && cs.clip !== "auto")) {
          const b = e.getBoundingClientRect();
          left = Math.max(left, b.left); top = Math.max(top, b.top); right = Math.min(right, b.right); bottom = Math.min(bottom, b.bottom);
        }
      }
      left = Math.max(left, 0); top = Math.max(top, 0); right = Math.min(right, innerWidth); bottom = Math.min(bottom, innerHeight);
      return right - left > 1 && bottom - top > 1 ? { left, top, right, bottom } : null;
    };
    const boxes = [];
    const walk = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let n, i = 0;
    while ((n = walk.nextNode())) {
      const text = n.textContent.replace(/\s+/g, " ").trim();
      if (!text) continue;
      const el = n.parentElement;
      if (!el.checkVisibility({ opacityProperty: true, visibilityProperty: true })) continue;
      const range = document.createRange(); range.selectNodeContents(n);
      for (const r of range.getClientRects()) {
        if (r.width < 1 || r.height < 1) continue;
        const c = clipBox(el, r);
        if (c) boxes.push({ node: i, el, text: text.slice(0, 50), pin: pinned(el), ...c });
      }
      i++;
    }
    // What covers a point of a box: the layers above the element of the box in the paint order, with their names.
    const layersAbove = (b, x, y) => {
      const stack = document.elementsFromPoint(x, y);
      const above = [];
      for (const e of stack) {
        if (e === b.el || b.el.contains(e)) break;
        if (e.contains(b.el)) continue;
        above.push(e);
      }
      return above;
    };
    const name = (e) => `<${e.tagName.toLowerCase()}${e.getAttribute("aria-label") ? " " + e.getAttribute("aria-label") : ""}${e.className && typeof e.className === "string" ? " ." + e.className.split(/\s+/).slice(0, 3).join(".") : ""}>`;
    const showThrough = [], hidden = [];
    for (const b of boxes) {
      if (b.pin) continue;
      const pts = [[(b.left + b.right) / 2, (b.top + b.bottom) / 2], [b.left + 2, (b.top + b.bottom) / 2], [b.right - 2, (b.top + b.bottom) / 2]];
      for (const [x, y] of pts) {
        const above = layersAbove(b, x, y);
        const bar = above.map(pinned).find(Boolean);
        if (!bar) continue;
        const opaque = above.some((e) => alpha(getComputedStyle(e).backgroundColor) >= 1 && opacityChain(e) >= 1);
        (opaque ? hidden : showThrough).push(`"${b.text}" under ${name(bar)} (${getComputedStyle(bar).position}) at ${Math.round(x)},${Math.round(y)}${opaque ? "" : "; layers above: " + above.slice(0, 3).map((e) => name(e) + " bg " + getComputedStyle(e).backgroundColor).join(", ")}`);
        break;
      }
    }
    const overlaps = [];
    for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
      const p = boxes[a], q = boxes[c];
      if (p.node === q.node) continue;
      const w = Math.min(p.right, q.right) - Math.max(p.left, q.left);
      const h = Math.min(p.bottom, q.bottom) - Math.max(p.top, q.top);
      if (!(w > 3 && h > 3 && h > 0.25 * Math.min(p.bottom - p.top, q.bottom - q.top))) continue;
      // A box of the page under an opaque bar does not show, so it cannot overlap the text of the bar.
      if (!!p.pin !== !!q.pin) {
        const content = p.pin ? q : p;
        const x = (Math.max(p.left, q.left) + Math.min(p.right, q.right)) / 2, y = (Math.max(p.top, q.top) + Math.min(p.bottom, q.bottom)) / 2;
        const above = layersAbove(content, x, y);
        if (above.some((e) => alpha(getComputedStyle(e).backgroundColor) >= 1 && opacityChain(e) >= 1)) continue;
      }
      overlaps.push(`"${p.text}" overlaps "${q.text}" by ${w.toFixed(0)}x${h.toFixed(0)} px`);
    }
    return { scope: root === document.body ? "viewport" : "viewport, open dialog", scrollY: Math.round(scrollY), boxes: boxes.length, overlaps, showThrough, hidden };
  });
}

/* The context of one test run in one viewport and theme. Each shot writes its PNG and one line of the overlap file. */
function makeShot(folder, prefix, view, theme, page) {
  return async (name, opts = {}) => {
    const file = `${prefix}${name}-${view.w}x${view.h}-${theme}.png`;
    const dialog = await page.locator('[role=dialog]:visible').count();
    if (!dialog) await scrollPass(page);
    else await pause(page, 600);
    // A page shot is full page. A sheet shot is the viewport, because the sheet is fixed over the page.
    await page.screenshot({ path: join(folder, file), fullPage: !dialog && !opts.viewport });
    const check = await overlapCheck(page);
    const line = `${file}: scope ${check.scope}, ${check.boxes} text boxes, ${check.overlaps.length} overlaps, ${check.covered.length} covered by a fixed bar`;
    appendFileSync(join(folder, `${prefix}overlap.txt`), [line, ...check.overlaps.map((o) => "  overlap: " + o), ...check.covered.map((c) => "  covered: " + c)].join("\n") + "\n");
    // A sheet with more content than the viewport gets a second shot after a scroll of its own content to the end.
    if (dialog && opts.sheetEnd !== false) {
      const scrolled = await page.evaluate(() => {
        const d = [...document.querySelectorAll('[role=dialog]')].at(-1);
        const s = d && [d, ...d.querySelectorAll("*")].find((e) => e.scrollHeight > e.clientHeight + 4 && /auto|scroll/.test(getComputedStyle(e).overflowY));
        if (!s) return false; s.scrollTop = s.scrollHeight; return true;
      });
      if (scrolled) { await pause(page, 600); await page.screenshot({ path: join(folder, `${prefix}${name}-end-${view.w}x${view.h}-${theme}.png`) }); }
    }
  };
}

const TESTS = (await import("./tests.mjs")).default;

const browser = await webkit.launch();
const round = Date.now();
try {
  for (const id of ids) {
    const test = TESTS[id];
    if (!test) throw new Error("no test " + id);
    // A variant run writes into the folder of its test, such as AT-37 for AT-37-variant.
    const folder = join(EVIDENCE, test.folder ?? id);
    mkdirSync(folder, { recursive: true });
    const prefix = test.prefix ?? "";
    writeFileSync(join(folder, `${prefix}overlap.txt`), `Overlap check of ${id}, WebKit, client ${client}. Rule: no visible text box overlaps another by more than 3 px both ways; at the top of the page no text sits under a bar in the upper half of the viewport; at the end of the page no text sits under a bar in the lower half of the viewport; in an open sheet no text sits under a fixed bar outside the sheet.\n`);
    const begin = Date.now();
    for (const view of VIEWS) for (const theme of THEMES) {
      const ctx = await browser.newContext({ ...devices[view.device], viewport: { width: view.w, height: view.h }, reducedMotion: "no-preference" });
      await ctx.addInitScript(([team, theme]) => {
        localStorage.setItem("cpc.theme", theme);
        if (team) localStorage.setItem("cpc.your-team", team);
        localStorage.setItem("cpc.tour-seen", "1");
        localStorage.setItem("cpc.passphrase", "localtest");
        localStorage.setItem("cpc.announcement.the-race-2026", "seen");
      }, [test.noTeam ? null : YOUR_TEAM[client], theme]);
      const page = await ctx.newPage();
      const calls = [];
      page.on("response", async (res) => {
        if (!res.url().startsWith(api) || res.request().method() !== "POST") return;
        let body = ""; try { body = await res.text(); } catch {}
        calls.push({ url: res.url(), status: res.status(), request: res.request().postData(), response: body });
      });
      page.on("requestfailed", (req) => { if (req.url().startsWith(api)) calls.push({ url: req.url(), failed: req.failure()?.errorText, request: req.postData() }); });
      try {
        await page.goto(site + test.route, { waitUntil: "networkidle" });
        await pause(page, 1000);
        const shot = makeShot(folder, prefix, view, theme, page);
        // A viewport shot at the scroll of the moment, with the viewport check of viewCheck on the same frame.
        const viewShot = async (name) => {
          const fileName = `${prefix}${name}-${view.w}x${view.h}-${theme}.png`;
          await page.screenshot({ path: join(folder, fileName) });
          const c = await viewCheck(page);
          appendFileSync(join(folder, `${prefix}overlap.txt`), [`${fileName}: scope ${c.scope} at scrollY ${c.scrollY}, ${c.boxes} text boxes, ${c.overlaps.length} overlaps, ${c.showThrough.length} show through a fixed or sticky bar, ${c.hidden.length} hidden under an opaque bar`, ...c.overlaps.map((o) => "  overlap: " + o), ...c.showThrough.map((s) => "  shows through: " + s), ...c.hidden.map((s) => "  hidden: " + s)].join("\n") + "\n");
        };
        await test.run({ page, shot, viewShot, view, theme, folder, prefix, pause: (ms) => pause(page, ms), note: (name, data) => appendFileSync(join(folder, `${prefix}${name}`), `--- ${view.w}x${view.h} ${theme}\n${typeof data === "string" ? data : JSON.stringify(data, null, 1)}\n`) });
        await pause(page, 500);
        if (test.calls) writeFileSync(join(folder, `${prefix}api-${view.w}x${view.h}-${theme}.json`), JSON.stringify(calls, null, 1));
      } catch (e) {
        throw new Error(`${id} ${view.w}x${view.h} ${theme}: ${e.message}`);
      } finally { await ctx.close(); }
    }
    console.log(`${id} ${test.route} ${client}: ${((Date.now() - begin) / 1000).toFixed(1)} s`);
  }
} finally { await browser.close(); }
console.log(`Total: ${ids.length} tests in ${((Date.now() - round) / 1000).toFixed(1)} s`);
