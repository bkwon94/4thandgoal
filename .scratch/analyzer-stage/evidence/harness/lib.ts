import { expect, type Page, type Browser, type BrowserContext } from "@playwright/test";
import { mkdirSync, writeFileSync, appendFileSync } from "node:fs";
import { join } from "node:path";
import { openPage, scanHeroPixels } from "../../ev2/apps/site/e2e/floor";
import { serveDir } from "../../ev2/apps/site/e2e/serve";
export { openPage, scanHeroPixels, serveDir };
export const EV = process.env.EV_OUT ?? "/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/analyzer-stage/.scratch/analyzer-stage/evidence";
export const SCR = "/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/aefcbbd4-1bb0-4c65-999d-49283a8a0c92/scratchpad";
export const BASE = "http://127.0.0.1:4173";
export const HERO = 'section[aria-label="Trade Analyzer"]';
export const WAIT_HERO = 'section[aria-label="Grading the Trade"]';
export const READ_HERO = 'section[aria-label="The Read"]';
export const WIDTHS = [375, 768, 1280];
export const THEMES = ["light", "dark"] as const;
export const T_QUERY = "?team=6&with=12&give=8151&get=6801,12490";
export function dir(at: string) { const d = join(EV, at); mkdirSync(d, { recursive: true }); return d; }
export function log(at: string, line: string) { const d = dir(at); appendFileSync(join(d, "output.txt"), line + "\n"); console.log(`${at}: ${line}`); }
export function reset(at: string, cmd: string) { writeFileSync(join(dir(at), "output.txt"), `$ ${cmd}\n`); }
/* Opens the analyzer with the passphrase stored and the theme set. A held analyze route keeps the real request until release. */
export async function openAnalyzer(page: Page, query: string, theme: "light" | "dark") {
  await page.addInitScript(() => localStorage.setItem("cpc.passphrase", "localtest"));
  // A first load can stall on an off-machine request, so the load gets 30 s and one retry. The retry is part of the
  // instrument and logs the requests that were still open.
  page.setDefaultNavigationTimeout(30000);
  const open = new Set<string>();
  page.on("request", (r) => open.add(r.url()));
  page.on("requestfinished", (r) => open.delete(r.url()));
  page.on("requestfailed", (r) => open.delete(r.url()));
  const capped = () => Promise.race([openPage(page, `${BASE}/analyze/${query}`, theme), new Promise<never>((_, no) => setTimeout(() => no(new Error("openPage took over 30 s")), 30000))]);
  try { await capped(); } catch (e) {
    console.log(`openAnalyzer: the first load failed (${String(e).split("\n")[0]}); open requests: ${[...open].join(", ")}; retry`);
    await openPage(page, `${BASE}/analyze/${query}`, theme);
  }
  await expect(page.getByRole("button", { name: "Grade the Trade" }).or(page.getByRole("button", { name: "Find a Trade" })).first()).toBeVisible({ timeout: 60000 });
  // The grade bar is ready only when the teams are in. A query with players fills a whole trade, so the tap waits for the bar.
  if (/[?&](give|get)=/.test(query)) await expect(page.getByRole("button", { name: "Grade the Trade" })).toBeEnabled({ timeout: 60000 });
}
export type Held = { release: () => Promise<void>; seen: () => boolean; sentAt: () => number | null };
/* Holds the real analyze POST, then passes it on to the local API on release. */
export async function holdAnalyze(page: Page): Promise<Held> {
  let held: (() => Promise<void>) | null = null;
  let sent: number | null = null;
  await page.route(/\/analyze$/, async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    await new Promise<void>((done) => { held = async () => { sent = Date.now(); await route.continue(); done(); }; });
  });
  return { release: async () => { while (!held) await page.waitForTimeout(50); await held(); }, seen: () => held !== null, sentAt: () => sent };
}
export async function settle(page: Page) {
  const frames = () => page.locator(`canvas[data-hero-mesh]`).first().evaluate((el) => Number((el as HTMLCanvasElement).dataset.meshFrames ?? 0)).catch(() => 0);
  let before = -1;
  for (let now = await frames(); now !== before; now = await frames()) { before = now; await page.waitForTimeout(500); }
}
export async function newPage(browser: Browser, width: number, opts: Record<string, unknown> = {}): Promise<{ ctx: BrowserContext; page: Page }> {
  const ctx = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: "no-preference", ...opts });
  const page = await ctx.newPage();
  // Each action and wait of the harness gets 60 s, so a stalled step fails with its name and does not hang the run.
  page.setDefaultTimeout(60000);
  return { ctx, page };
}
/* Records each request and response of the API in a list, for a network log. */
export function netLog(page: Page) {
  const rows: string[] = [];
  const t0 = Date.now();
  page.on("request", (r) => { if (r.url().includes(":8080")) rows.push(`${Date.now() - t0} ms  -> ${r.method()} ${r.url()}`); });
  page.on("response", async (r) => {
    if (!r.url().includes(":8080")) return;
    const h = await r.allHeaders();
    rows.push(`${Date.now() - t0} ms  <- ${r.status()} ${r.request().method()} ${r.url()}  content-type: ${h["content-type"] ?? "-"}  transfer-encoding: ${h["transfer-encoding"] ?? "-"}`);
  });
  return rows;
}
/* The watch of the reveal of the e2e spec, copied: the first frame at which each part is at rest, and the mesh samples. */
export type Reveal = { lean: number | null; scale: number | null; case: number | null; tabs: number | null; mesh: { at: number; flash: number; pulls: number[] }[]; fade: number[]; leanMove: number };
export const watchReveal = (page: Page) =>
  page.evaluate((hero) => {
    const w = window as unknown as { reveal: Promise<unknown> };
    w.reveal = new Promise((done) => {
      const t: Record<string, unknown> = { lean: null, scale: null, case: null, tabs: null, mesh: [], fade: [], leanMove: 0 };
      const mesh = t.mesh as { at: number; flash: number; pulls: number[] }[];
      const fade = t.fade as number[];
      let shown: number | null = null;
      const seen = (el: Element | null) => { let o = 1; for (let up = el; up; up = up.parentElement) o *= parseFloat(getComputedStyle(up).opacity); return el ? o : 0; };
      const matrix = (el: Element) => new DOMMatrixReadOnly(getComputedStyle(el).transform === "none" ? undefined : getComputedStyle(el).transform);
      const sharp = (el: Element) => ["none", "blur(0px)"].includes(getComputedStyle(el).filter);
      const still = (el: Element | null) => !!el && seen(el) >= 0.99 && Math.abs(matrix(el).f) < 0.5 && sharp(el);
      const mark = (key: string, ok: boolean) => { if (ok && t[key] === null) t[key] = Date.now(); };
      const tick = () => {
        const now = Date.now();
        const read = document.querySelector(hero);
        if (read) {
          shown ??= now;
          const lean = read.querySelector('[data-stable-id="lean-word"]');
          if (lean) t.leanMove = Math.max(t.leanMove as number, Math.abs(matrix(lean).f));
          mark("lean", still(lean));
          const fill = read.querySelector('[data-reveal-part="scale"]');
          mark("scale", !!fill && seen(fill) >= 0.99 && matrix(fill).a >= 0.99);
          mark("case", still(read.querySelector(".t-stagger-line")));
          const tabs = document.querySelector('[role="tablist"][aria-label="The sides"]');
          mark("tabs", !!tabs && seen(tabs) >= 0.99 && sharp(tabs.closest(".t-skel-content") ?? tabs));
          const canvas = read.querySelector<HTMLCanvasElement>("canvas[data-hero-mesh]");
          if (canvas?.dataset.meshFlash !== undefined) mesh.push({ at: now, flash: Number(canvas.dataset.meshFlash), pulls: (canvas.dataset.meshPulls ?? "").split(",").filter(Boolean).map(Number) });
          fade.push(parseFloat(getComputedStyle(read.closest("[data-trade-key]") ?? read).opacity));
          if (now - shown > 2500) return done(t);
        }
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }, READ_HERO);
export const revealOf = (page: Page) => page.evaluate(() => (window as unknown as { reveal: Promise<unknown> }).reveal) as Promise<Reveal>;
/*
 * The watch of the wait: it taps the button in the page, so the time 0 is the tap, and it records on each frame the
 * text of the live stage line, the time the first line shows with a moving mesh, the pulls of the mesh, and the time
 * the headshot tokens come to rest.
 */
export const startWait = (page: Page, tokens: number, how: "click" | "none" = "click") =>
  page.evaluate(([hero, want, how]) => {
    const w = window as unknown as Record<string, unknown>;
    const lines: { t: number; text: string }[] = [];
    const pulls: { t: number; p: number[] }[] = [];
    const st = { t0: performance.now(), lines, pulls, firstLine: null as number | null, meshMoves: null as number | null, tokensRest: null as number | null, tokenCount: 0 };
    w.wait = st;
    const btn = [...document.querySelectorAll("button")].find((b) => b.textContent?.trim() === "Grade the Trade") as HTMLButtonElement;
    let last: number | null = null;
    const check = () => {
      const t = performance.now() - st.t0;
      const line = document.querySelector(`${hero} .t-think-text:not(.is-exit)`);
      const text = line?.textContent ?? "";
      if (text && lines.at(-1)?.text !== text) lines.push({ t, text });
      const canvas = document.querySelector<HTMLCanvasElement>(`${hero} canvas[data-hero-mesh]`);
      if (canvas) pulls.push({ t, p: (canvas.dataset.meshPulls ?? "").split(",").filter(Boolean).map(Number) });
      if (st.meshMoves === null && text === "Weighing the sides" && canvas && canvas.width > 1) {
        st.firstLine ??= t;
        const data = canvas.getContext("2d")!.getImageData(0, 0, canvas.width, canvas.height).data;
        let sum = 0;
        for (let k = 0; k < data.length; k += 4) sum += data[k] * 3 + data[k + 1] * 5 + data[k + 3] * 7;
        if (last !== null && sum !== last) st.meshMoves = t;
        last = sum;
      }
      if (st.tokensRest === null) {
        const tokens = [...document.querySelectorAll(`${hero} [data-mesh-hole][title]`)];
        st.tokenCount = tokens.length;
        const still = tokens.filter((el) => {
          const s = getComputedStyle(el);
          const m = new DOMMatrixReadOnly(s.transform === "none" ? undefined : s.transform);
          return Math.abs(m.f) <= 0.01 && Math.abs(m.a - 1) <= 0.001 && ["none", "blur(0px)"].includes(s.filter) && parseFloat(s.opacity) >= 0.99;
        }).length;
        if (want > 0 && tokens.length === want && still === want) st.tokensRest = t;
      }
      if (t < 40000) requestAnimationFrame(check);
    };
    if (how === "click") btn.click();
    requestAnimationFrame(check);
  }, [WAIT_HERO, tokens, how] as const);
export const waitState = (page: Page) => page.evaluate(() => { const w = (window as unknown as Record<string, any>).wait; return { ...w, now: performance.now() - w.t0 }; });
export async function untilElapsed(page: Page, ms: number) {
  for (;;) { const { now } = await waitState(page); if (now >= ms) return now; await page.waitForTimeout(Math.min(100, ms - now)); }
}
export const elapsed = async (page: Page) => (await waitState(page)).now as number;
/* Trade B through the Stack, as the e2e spec opens it. A copy of the one in held.spec.ts, so a spec can use it alone. */
export async function openTradeB(page: Page, theme: "light" | "dark") {
  await openAnalyzer(page, "?team=1&with=3&get=11560,1466,2449,3198,4034&give=11584", theme);
  await page.getByRole("button", { name: "Add a team" }).click();
  await page.getByRole("dialog").getByRole("button", { name: /All You Need Is Love/ }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  const pick = async (side: string, from: string, names: string[]) => {
    await page.getByRole("button", { name: `Add a player ${side} gets` }).click();
    const sheet = page.getByRole("dialog");
    await sheet.getByRole("tab", { name: from }).click();
    for (const name of names) await sheet.getByRole("checkbox", { name: new RegExp(name) }).click();
    await sheet.getByRole("button", { name: /^Done/ }).click();
    await expect(page.getByRole("dialog")).toHaveCount(0);
  };
  await pick("Team Three", "The Blue Tent", ["Rashee Rice", "Brock Bowers"]);
  await pick("Team Two", "All You Need Is Love", ["Ashton Jeanty", "Jeremiyah Love"]);
}
/*
 * The watch of the light of the read mesh in each row, copied from apps/site/e2e/analyzer-stage.spec.ts. Near the peak
 * of the flash and near the deepest dip it sums the light of the canvas inside the box of each row, and 2.5 s after the
 * read hero shows it sums the light of the flat mesh at rest. The light of a pixel is its color times its alpha.
 */
export type RowLight = { flash: { flash: number; sums: number[] }; dip: { pull: number; sums: number[] }; rest: number[] };
export const watchRowLight = (page: Page) =>
  page.evaluate((hero) => {
    const w = window as unknown as { rowLight: Promise<unknown> };
    w.rowLight = new Promise((done) => {
      let shown: number | null = null;
      let best = { flash: 0, sums: [] as number[] };
      let deepest = { pull: 0, sums: [] as number[] };
      const sums = (canvas: HTMLCanvasElement) => {
        const origin = canvas.getBoundingClientRect();
        const scale = canvas.width / origin.width;
        const ctx = canvas.getContext("2d")!;
        return [...document.querySelectorAll(`${hero} [data-mesh-anchor]`)].map((row) => {
          const box = row.getBoundingClientRect();
          const x = Math.round((box.left - origin.left) * scale);
          const y = Math.round((box.top - origin.top) * scale);
          const data = ctx.getImageData(x, y, Math.round(box.width * scale), Math.round(box.height * scale)).data;
          let sum = 0;
          for (let k = 0; k < data.length; k += 4) sum += ((data[k] + data[k + 1] + data[k + 2]) * data[k + 3]) / 255;
          return sum;
        });
      };
      const total = (list: number[]) => list.reduce((a, b) => a + b, 0);
      const tick = () => {
        const canvas = document.querySelector<HTMLCanvasElement>(`${hero} canvas[data-hero-mesh]`);
        if (canvas && canvas.width > 1) {
          shown ??= Date.now();
          const flash = Number(canvas.dataset.meshFlash ?? 0);
          const pull = Math.max(0, ...(canvas.dataset.meshPulls ?? "").split(",").filter(Boolean).map(Number));
          if (flash > 0.5) { const now = sums(canvas); if (total(now) > total(best.sums)) best = { flash, sums: now }; }
          if (pull > 0.45) { const now = sums(canvas); if (total(now) > total(deepest.sums)) deepest = { pull, sums: now }; }
          if (Date.now() - shown > 2500) return done({ flash: best, dip: deepest, rest: sums(canvas) });
        }
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }, READ_HERO);
export const rowLightOf = (page: Page) => page.evaluate(() => (window as unknown as { rowLight: Promise<unknown> }).rowLight) as Promise<RowLight>;
/*
 * The plate scan of AT-17. For each hero text it walks from the text up to the hero and names each element with a fill
 * on the way, with its kind. A plate box is the old plate utility: a fill of the band color with a box shadow, or the
 * class `plate`. A record pill is a `[data-result]` chip. A button is an `a`, a `button`, or a `[role=button]`. A stat
 * tile is a box of the hero tone of Tile, with a label and a number. Any other fill is "other fill".
 */
export const plateScan = (page: Page, heroSel: string) =>
  page.locator(heroSel).first().evaluate((h) => {
    const probe = document.createElement("div");
    probe.style.backgroundColor = "var(--color-band)";
    h.appendChild(probe);
    const band = getComputedStyle(probe).backgroundColor;
    probe.remove();
    const kindOf = (el: Element, cs: CSSStyleDeclaration) => {
      if (el.classList.contains("plate") || (cs.backgroundColor === band && cs.boxShadow !== "none")) return "plate box";
      if (el.hasAttribute("data-result")) return "record pill";
      if (el.matches("a, button, [role=button]")) return "button";
      if (el.classList.contains("bg-chip-dark") && el.children.length >= 2) return "stat tile";
      return "other fill";
    };
    const rows: { text: string; behind: string; kind: string }[] = [];
    for (const el of h.querySelectorAll("*")) {
      if (el.closest("svg")) continue;
      const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent!.trim());
      if (!own) continue;
      const cs0 = getComputedStyle(el);
      if (cs0.display === "none" || cs0.visibility === "hidden") continue;
      const text = el.textContent!.trim().replace(/\s+/g, " ").slice(0, 40);
      const fills: string[] = [];
      const kinds: string[] = [];
      for (let up: Element | null = el; up && up !== h; up = up.parentElement) {
        const cs = getComputedStyle(up);
        if (cs.backgroundColor !== "rgba(0, 0, 0, 0)" || cs.backgroundImage !== "none" || cs.backdropFilter !== "none") {
          const kind = kindOf(up, cs);
          kinds.push(kind);
          fills.push(`${up.tagName.toLowerCase()}${up.getAttribute("class") ? ` class "${up.getAttribute("class")!.slice(0, 60)}"` : ""} bg ${cs.backgroundColor}${cs.backgroundImage !== "none" ? ` img ${cs.backgroundImage.slice(0, 24)}` : ""}${cs.boxShadow !== "none" ? ` shadow ${cs.boxShadow.slice(0, 40)}` : ""} [${kind}]`);
        }
      }
      rows.push({ text, behind: fills.length ? fills.join(" < ") : "the hero art only", kind: kinds.length ? kinds[0] : "no fill" });
    }
    return { band, rows };
  });
export const fmtPlate = (scan: { band: string; rows: { text: string; behind: string; kind: string }[] }) => {
  const count = (k: string) => scan.rows.filter((r) => r.kind === k).length;
  return `band color ${scan.band}; ${scan.rows.length} hero texts: plate box ${count("plate box")}, record pill ${count("record pill")}, stat tile ${count("stat tile")}, button ${count("button")}, other fill ${count("other fill")}, no fill ${count("no fill")}\n    ${scan.rows.map((r) => `"${r.text}" | ${r.kind} | ${r.behind}`).join("\n    ")}`;
};
