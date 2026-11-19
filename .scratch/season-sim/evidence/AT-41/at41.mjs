/**
 * The WebKit evidence of AT-41 of season-sim, a frame sampler of place and opacity, on the cpc export of 4c485cd8, the fix of AT-41 on the branch season-sim-fix-f. From replay.mjs: It shoots each screen of "Sim week 11" and of
 * "Sim the season" at 390x660, 810x980, 1080x740, and 1280x800 in both themes, with the overlap check of ACCEPTANCE.md.
 * Modes: "screens" (AT-38, AT-39), "whatif" (AT-40, a real call to the local API), "motion" (AT-41, a frame check).
 */
import { createRequire } from "node:module";
import { mkdirSync, writeFileSync } from "node:fs";

const require = createRequire("/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/season-sim-fix-f/apps/site/package.json");
const { webkit, devices } = require("@playwright/test");

const EV = "/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/7169efb8-161d-49b8-b8f0-64097daad76e/scratchpad/ev41f/evidence";
let OUT = `${EV}/AT-38`;
const BASE = "http://127.0.0.1:4191/sim/2026/";
const MODE = process.argv[2] ?? "screens";
for (const at of ["AT-38", "AT-39", "AT-40", "AT-41"]) mkdirSync(`${EV}/${at}`, { recursive: true });

const SIZES = [
  ["390x660", "iPhone 15", 390, 660],
  ["810x980", "iPad (gen 7)", 810, 980],
  ["1080x740", "iPad (gen 7) landscape", 1080, 740],
  ["1280x800", null, 1280, 800],
];
const THEMES = ["light", "dark"];

/* The overlap check: no text box overlaps another, no text leaves the screen, and no box covers a text in view.
   With the replay open, the check reads the stage and the site band, because the stage covers the page on purpose.
   It also checks that the stage does not scroll, and that the body of the stage ends above the row of the controls. */
const probe = () => {
  const stage = document.querySelector('[aria-label="Sim replay"]');
  const band = document.querySelector("body > header, header.sticky");
  const roots = stage ? [stage, band].filter(Boolean) : [document.body];
  const items = [];
  const walk = (el) => {
    if (el.closest("[aria-hidden=true],.sr-only,nextjs-portal")) return;
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden" || cs.opacity === "0") return;
    const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    const r = el.getBoundingClientRect();
    if ((own || el.tagName === "BUTTON") && r.width > 1 && r.height > 1)
      items.push({ el, r, own, btn: el.tagName === "BUTTON", t: (el.textContent || "").trim().slice(0, 30) });
    for (const c of el.children) walk(c);
  };
  roots.forEach(walk);
  const bad = [];
  const vh = innerHeight, vw = innerWidth;
  const bandBottom = band ? band.getBoundingClientRect().bottom : 0;
  const inBand = (x) => band !== null && band.contains(x.el);
  for (const x of items) x.hidden = !inBand(x) && x.r.top < bandBottom - 1;
  if (stage) {
    // The stage sits under the band and inside the screen, and nothing in it scrolls.
    const s = stage.getBoundingClientRect();
    if (Math.abs(s.top - bandBottom) > 1) bad.push(`stage top ${s.top} is not the band bottom ${bandBottom}`);
    if (s.bottom > vh + 1) bad.push(`stage bottom ${s.bottom} past the screen ${vh}`);
    for (const el of [stage, ...stage.querySelectorAll("*")]) {
      // A screen reader text clips to 1 px on purpose, so it is no scroll.
      if (el.closest(".sr-only")) continue;
      if (el.scrollHeight > el.clientHeight + 1 && getComputedStyle(el).overflowY !== "visible" && el.clientHeight > 0)
        bad.push(`scrolls: ${el.tagName}.${String(el.className).slice(0, 30)} ${el.scrollHeight}/${el.clientHeight}`);
    }
    const body = stage.querySelector('[data-testid="stage-body"]');
    const controls = stage.querySelector('[aria-label="Replay controls"]');
    const b = body.getBoundingClientRect(), c = controls.getBoundingClientRect();
    if (b.bottom > c.top + 1) bad.push(`body ${b.bottom} runs into the controls ${c.top}`);
    // Each box of the body ends above the controls, so no control covers the stage.
    for (const el of body.querySelectorAll("*")) {
      const r = el.getBoundingClientRect();
      if (r.height > 0 && r.bottom > c.top + 1 && getComputedStyle(el).opacity !== "0") { bad.push(`"${(el.textContent || "").trim().slice(0, 20)}" under the controls`); break; }
    }
  }
  for (let i = 0; i < items.length; i++) {
    const a = items[i];
    if (a.hidden) continue;
    if (a.own && (a.r.right > vw + 1 || a.r.left < -1)) bad.push(`offscreen-x "${a.t}"`);
    if (a.own && a.r.top >= 0 && a.r.bottom <= vh) {
      const cx = a.r.left + a.r.width / 2, cy = a.r.top + a.r.height / 2;
      const top = document.elementFromPoint(cx, cy);
      if (top && !a.el.contains(top) && !top.contains(a.el)) bad.push(`covered "${a.t}" by ${top.tagName} "${(top.textContent || "").trim().slice(0, 20)}"`);
    }
    for (let j = i + 1; j < items.length; j++) {
      const b = items[j];
      if (b.hidden || inBand(a) !== inBand(b)) continue;
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      const w = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
      const h = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
      if (w > 1 && h > 1 && (a.own || a.btn) && (b.own || b.btn)) bad.push(`overlap "${a.t}" / "${b.t}"`);
    }
  }
  return { bad, scrollW: document.documentElement.scrollWidth, vw, scrollY: scrollY, docScroll: document.documentElement.scrollHeight > innerHeight };
};

const logs = {};
const notesBy = {};
/* The shot name of the rule of the evidence: <name>-<width>x<height>-<theme>. */
const rename = (n) => n.replace(/^at41-(reduced|full)-(light|dark)-(.+)$/, "motion-$1-$3-390x660-$2").replace(/^(at40-)?(\d+x\d+)-(light|dark)-(.+)$/, "$1$4-$2-$3");
let fails = 0;

/* The check of one screen of the replay: one probe, with no scroll, because the stage never scrolls. A page check
   scrolls the page in steps, so a box below the first screen gets the same check. */
async function check(page, name, { scroll = false } = {}) {
  name = rename(name);
  const bad = new Set();
  if (scroll) {
    const height = await page.evaluate(() => document.documentElement.scrollHeight);
    const vh = page.viewportSize().height;
    for (let y = 0; y < height; y += Math.floor(vh * 0.8)) {
      await page.evaluate((top) => window.scrollTo(0, top), y);
      await page.waitForTimeout(120);
      const r = await page.evaluate(probe);
      r.bad.forEach((b) => bad.add(b));
      if (r.scrollW > r.vw + 1) bad.add(`page scrolls sideways ${r.scrollW}/${r.vw}`);
    }
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(150);
  } else {
    const r = await page.evaluate(probe);
    r.bad.forEach((b) => bad.add(b));
    if (r.scrollW > r.vw + 1) bad.add(`page scrolls sideways ${r.scrollW}/${r.vw}`);
    // The page under the layer cannot scroll while the replay is open.
    const moved = await page.evaluate(() => {
      const before = scrollY;
      scrollBy(0, 300);
      const after = scrollY;
      scrollTo(0, before);
      return { before, after, overflow: document.documentElement.style.overflow };
    });
    if (moved.overflow !== "hidden") bad.add(`page overflow is "${moved.overflow}", not hidden`);
  }
  await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: scroll });
  const line = `${OUT.split("/").at(-1)}/${name}.png: ${bad.size ? `${bad.size} issues: ` + [...bad].slice(0, 6).join(" | ") : "no overlap, no cover, no side scroll, no scroll in the stage"}`;
  if (bad.size) fails++;
  (logs[OUT] ??= []).push(line);
  console.log(line);
}

const say = (page) => page.locator('[aria-label="Sim replay"] [role=status]');
async function until(page, text, extra) {
  await say(page).filter({ hasText: text }).waitFor({ timeout: 30000 });
  await page.waitForTimeout(extra);
}

async function open(browser, size, theme, { reduced = false } = {}) {
  const [, device, w, h] = size;
  const base = device ? devices[device] : {};
  const context = await browser.newContext({ ...base, viewport: { width: w, height: h }, colorScheme: theme, reducedMotion: reduced ? "reduce" : "no-preference" });
  await context.addInitScript(([t]) => {
    localStorage.setItem("cpc.theme", t);
    localStorage.setItem("cpc.your-team", "6");
    localStorage.setItem("cpc.announcement.season-sim-2026", "seen");
  }, [theme]);
  const page = await context.newPage();
  await page.goto(BASE, { waitUntil: "networkidle" });
  await page.getByRole("region", { name: "Your team" }).waitFor();
  await page.waitForTimeout(500);
  return { context, page };
}

const games = (page) => page.getByRole("list", { name: "Week 11 games" });
const tile = (page, name) =>
  page.getByRole("group", { name: "Results" }).locator("button", { has: page.locator(`[data-result-name]:text-is("${name}")`) });

const browser = await webkit.launch();
const notes = { push: (...l) => (notesBy[OUT] ??= []).push(...l), join: () => "" };
if (MODE === "screens") {
  for (const size of SIZES.filter((x) => !process.env.ONLY || x[0] === process.env.ONLY)) {
    for (const theme of THEMES) {
      const tag = `${size[0]}-${theme}`;
      const { context, page } = await open(browser, size, theme);
      await check(page, `${tag}-0-page`, { scroll: true });
      // AT-38: Sim week 11, Games then Standings.
      OUT = `${EV}/AT-38`;
      await page.getByRole("button", { name: "Sim week 11" }).click();
      await until(page, "Week 11 games", 3000);
      const first = await games(page).locator("li").first().innerText();
      const median = await page.locator('[aria-label="Sim replay"] p', { hasText: /^Median / }).allInnerTexts();
      notes.push(`${tag} week games: first row "${first.replace(/\n/g, " ")}", median lines ${JSON.stringify(median)}`);
      await check(page, `${tag}-1-week-games`);
      await until(page, "Standings after week 11", 1700);
      const rows = await page.getByRole("list", { name: "Standings" }).locator("li").allInnerTexts();
      notes.push(`${tag} week standings: ${JSON.stringify(rows.map((r) => r.replace(/\n/g, " ")))}`);
      await check(page, `${tag}-2-week-standings`);
      await page.getByRole("button", { name: "Games", exact: true }).click();
      await page.waitForTimeout(700);
      await check(page, `${tag}-3-week-games-again`);
      await page.getByRole("button", { name: "Close the replay" }).click();
      await page.getByRole("region", { name: "Sim replay" }).waitFor({ state: "detached" });
      // AT-39: Sim the season, Season, Playoffs one round at a time, Champion.
      OUT = `${EV}/AT-39`;
      await page.getByRole("button", { name: "Sim the season" }).click();
      await until(page, "Week 12 final", 750);
      await check(page, `${tag}-4-season-week-12`);
      await until(page, "The playoff field is set", 1000);
      await check(page, `${tag}-5-season-field-set`);
      await until(page, "Round 1 results", 1150);
      await check(page, `${tag}-6-playoffs-round-1`);
      await until(page, "Semifinal results", 1150);
      await check(page, `${tag}-7-playoffs-semifinal`);
      await until(page, "Final results", 1150);
      await check(page, `${tag}-8-playoffs-final`);
      await until(page, "wins the title in this run", 1600);
      const end = await page.locator('[aria-label="Sim replay"] [data-testid="stage-body"]').innerText();
      notes.push(`${tag} champion: ${end.replace(/\n/g, " | ")}`);
      await check(page, `${tag}-9-champion`);
      await context.close();
    }
  }
} else if (MODE === "whatif") {
  OUT = `${EV}/AT-40`;
  // AT-40: Bo Girds set to win week 11 and beat the median, with a real call to the local API.
  for (const size of SIZES) {
    for (const theme of THEMES) {
      const tag = `at40-${size[0]}-${theme}`;
      const { context, page } = await open(browser, size, theme);
      const answer = page.waitForResponse((r) => r.url().includes("/sim/what-if") && r.request().method() === "POST");
      await tile(page, "Win, beat median").click();
      const response = await answer;
      notes.push(`${tag} what-if ${response.status()} ${response.request().postData()}`);
      await page.getByRole("button", { name: /^Wk 12/ }).and(page.locator("[aria-current=page]")).waitFor();
      await page.getByRole("button", { name: /^Wk 11/ }).click();
      await page.waitForTimeout(400);
      await page.getByRole("button", { name: "Sim week 11" }).click();
      await until(page, "Week 11 games", 3000);
      const mine = await games(page).locator("li").first().textContent();
      const median = await page.locator('[aria-label="Sim replay"] p', { hasText: /^Median / }).innerText();
      notes.push(`${tag} games: first row "${mine}", "${median}"`);
      
      await check(page, `${tag}-1-games`);
      await until(page, "Standings after week 11", 1700);
      await check(page, `${tag}-2-standings`);
      await context.close();
    }
  }
} else {
  OUT = `${EV}/AT-41`;
  // AT-41: the motion check. A script reads the box of each element of the stage on each frame. A box that moves on
  // two frames in a row is a motion; a box that takes a new place on one frame is a jump, which a fade may hide.
  for (const reduced of [true, false]) {
    for (const theme of THEMES) {
      const tag = `at41-${reduced ? "reduced" : "full"}-${theme}`;
      const { context, page } = await open(browser, SIZES[0], theme, { reduced });
      // A frame sampler: on each frame it reads, for each element of the stage, its place (left, top), its size, and
      // its shown opacity (the product of its own and each parent's). It logs each change with the time from the tap.
      await page.evaluate(() => {
        window.__log = [];
        window.__t0 = null;
        const ids = new WeakMap();
        let next = 1;
        const last = new Map();
        const name = (el) => {
          if (!ids.has(el)) ids.set(el, next++);
          const label = el.getAttribute("aria-label") || el.getAttribute("role") || "";
          return `#${ids.get(el)} ${el.tagName.toLowerCase()}${label ? `[${label}]` : ""}.${String(el.className?.baseVal ?? el.className).split(" ").slice(0, 3).join(".")} "${(el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 24)}"`;
        };
        const shown = (el) => { let o = 1; for (let e = el; e; e = e.parentElement) o *= Number(getComputedStyle(e).opacity); return o; };
        const tick = (now) => {
          const stage = document.querySelector('[aria-label="Sim replay"]');
          if (stage && window.__t0 !== null) {
            const t = Math.round(now - window.__t0);
            for (const el of [stage, ...stage.querySelectorAll("*")]) {
              const r = el.getBoundingClientRect();
              const cs = getComputedStyle(el);
              const s = { x: Math.round(r.left * 10) / 10, y: Math.round(r.top * 10) / 10, w: Math.round(r.width * 10) / 10, h: Math.round(r.height * 10) / 10, o: Math.round(shown(el) * 1000) / 1000 };
              const was = last.get(el);
              if (!was) window.__log.push({ t, kind: "new", el: name(el), s, tr: cs.transitionProperty + " " + cs.transitionDuration, an: cs.animationName + " " + cs.animationDuration });
              else {
                const pos = was.x !== s.x || was.y !== s.y;
                const size = was.w !== s.w || was.h !== s.h;
                const op = was.o !== s.o;
                if (pos || size || op) window.__log.push({ t, kind: [pos && "pos", size && "size", op && "opacity"].filter(Boolean).join("+"), el: name(el), was, s, tr: cs.transitionProperty + " " + cs.transitionDuration, an: cs.animationName + " " + cs.animationDuration });
              }
              last.set(el, s);
            }
          }
          requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      });
      await page.getByRole("button", { name: "Sim the season" }).click();
      await page.evaluate(() => { window.__t0 = performance.now(); });
      await until(page, "Week 12 final", 750);
      await check(page, `${tag}-1-season`);
      await until(page, "Round 1 results", 1150);
      await check(page, `${tag}-2-playoffs`);
      await until(page, "wins the title in this run", 1600);
      await check(page, `${tag}-3-champion`);
      const log = await page.evaluate(() => window.__log);
      const fmt = (s) => `(x ${s.x}, y ${s.y}, w ${s.w}, h ${s.h}, opacity ${s.o})`;
      const lines = log.filter((e) => e.kind !== "new").map((e) => `t=${e.t}ms ${e.kind} ${e.el} ${fmt(e.was)} -> ${fmt(e.s)} transition: ${e.tr} animation: ${e.an}`);
      writeFileSync(`${OUT}/frames-${reduced ? "reduced" : "full"}-${theme}.txt`, `# Every change of place, size, or shown opacity of an element of the stage, frame by frame, from the tap on "Sim the season" (t=0) to the champion screen, at 390x660, ${reduced ? "reduced motion" : "full motion"}, ${theme}. New elements are counted, not listed.\n` + lines.join("\n") + "\n");
      // The summary: by element, its changes of place and the path of its opacity.
      const by = new Map();
      for (const e of log) { if (e.kind === "new") continue; const key = e.el.split(" ")[0]; (by.get(key) ?? by.set(key, []).get(key)).push(e); }
      const posEls = [...by].filter(([, es]) => es.some((e) => e.kind.includes("pos")));
      const sizeEls = [...by].filter(([, es]) => es.some((e) => e.kind.includes("size")));
      const opEls = [...by].filter(([, es]) => es.some((e) => e.kind.includes("opacity")));
      const between = (es) => es.filter((e) => e.kind.includes("opacity")).map((e) => e.s.o).filter((o) => o > 0 && o < 1).length;
      notes.push(`${tag}: ${log.filter((e) => e.kind === "new").length} new elements; ${posEls.length} elements change place; ${sizeEls.length} elements change size; ${opEls.length} elements change shown opacity, ${opEls.filter(([, es]) => between(es) > 0).length} of them on frames with a value between 0 and 1`);
      for (const [, es] of posEls) notes.push(`  place: ${es[0].el}: ` + es.filter((e) => e.kind.includes("pos")).slice(0, 6).map((e) => `t=${e.t}ms (${e.was.x}, ${e.was.y}) -> (${e.s.x}, ${e.s.y})`).join("; ") + ` | transition: ${es[0].tr} | animation: ${es[0].an}`);
      for (const [, es] of sizeEls.slice(0, 40)) notes.push(`  size: ${es[0].el}: ` + es.filter((e) => e.kind.includes("size")).slice(0, 4).map((e) => `t=${e.t}ms ${e.was.w}x${e.was.h} -> ${e.s.w}x${e.s.h}`).join("; "));
      for (const [, es] of opEls.slice(0, 60)) {
        const el = es[0].el;
        const path = es.filter((e) => e.kind.includes("opacity"));
        notes.push(`  opacity: ${el}: ${path.length} frames, t=${path[0].t}ms to t=${path.at(-1).t}ms, ${path[0].was.o} -> ${path.slice(0, 12).map((e) => e.s.o).join(" -> ")}${path.length > 12 ? " -> ... -> " + path.at(-1).s.o : ""} | transition: ${path[0].tr} | animation: ${path[0].an}`);
      }
      if (opEls.length > 60) notes.push(`  (${opEls.length - 60} more opacity elements in frames-${reduced ? "reduced" : "full"}-${theme}.txt)`);
      
      
      await context.close();
    }
  }
}
await browser.close();
const sfx = process.env.ONLY ? `-${process.env.ONLY}` : "";
for (const [d, l] of Object.entries(logs)) writeFileSync(`${d}/overlap${sfx}.txt`, l.join("\n") + "\n");
for (const [d, l] of Object.entries(notesBy)) writeFileSync(`${d}/frames-summary${sfx}.txt`, l.join("\n") + "\n");
console.log("summary written");
console.log("shots with issues", fails);
