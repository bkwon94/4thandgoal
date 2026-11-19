/**
 * Evidence instrument of the spec deadline-week: WebKit, a fixed clock, the Trade Wire route served from the recorded
 * Sleeper answer of trade W, and the real local API for every other call. It records measures and shots per AT-<n>.
 */
import { devices, expect, test } from "@playwright/test";
import { appendFileSync, createReadStream, existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";

const E = process.env.EVIDENCE_DIR;
const PHASE = process.env.PHASE; // off | on | lock | norcal
const OUT = process.env.SITE_OUT;
const SITE_PORT = Number(process.env.SITE_PORT);
const SITE = `http://127.0.0.1:${SITE_PORT}`;
const CACHE = process.env.RESULT_CACHE ?? "";
const ONLY = (process.env.ONLY ?? "").split(",").filter(Boolean);

const OPEN = "2026-11-21T09:55:00-05:00";
const LAST_HOURS = "2026-11-23T21:18:50-05:00";
const CLOSED = "2026-11-24T00:00:01-05:00";
const ENDED = "2026-11-25T00:00:01-05:00";
const TRADE_W = "1424578776058155008";
const OTHER = "1425209111854747648";
const fixture = (name) => JSON.parse(readFileSync(join(E, "fixtures", `${name}.json`), "utf8"));

const COMBOS = [375, 768, 1280].flatMap((width) => ["light", "dark"].map((theme) => ({ width, theme })));
const { defaultBrowserType: _b, ...IPHONE } = devices["iPhone 15"];
const CORS = { "access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "GET, POST, OPTIONS" };

test.use({ browserName: "webkit" });
test.describe.configure({ mode: "parallel" });

const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".woff2": "font/woff2", ".ico": "image/x-icon", ".txt": "text/plain; charset=utf-8" };
// The export is served by serve.mjs on SITE_PORT, one process for all workers. A missing path gets 404.html with 404.

function dir(at) {
  const d = join(E, at);
  mkdirSync(d, { recursive: true });
  return d;
}
function note(at, file, value) {
  appendFileSync(join(dir(at), file), `${typeof value === "string" ? value : JSON.stringify(value)}\n`);
}
function fresh(at, file) {
  writeFileSync(join(dir(at), file), "");
}
const shotPath = (at, name, c) => join(dir(at), `${name ? `${name}-` : ""}${c.width}-${c.theme}.png`);

/* The Trade Wire route of the page answers from `source()`, which gives the status and the body. Each call is logged. */
async function serveWire(page, source, log = []) {
  await page.route(/\/deadline\/trades/, async (route) => {
    if (route.request().method() === "OPTIONS") return route.fulfill({ status: 204, headers: CORS });
    const { status, body } = source();
    log.push({ at: new Date().toISOString(), ms: Date.now(), status, trades: body?.trades?.length ?? null });
    return route.fulfill({ status, headers: CORS, contentType: "application/json", body: JSON.stringify(body ?? {}) });
  });
  return log;
}
const wireOf = (name) => () => ({ status: 200, body: fixture(name) });

async function newPage(browser, c, extra = {}) {
  const context = await browser.newContext({ viewport: { width: c.width, height: 900 }, reducedMotion: "no-preference", ...extra });
  return context.newPage();
}

/* Opens `path` at the clock `time` in the theme of `c`. `ticks` lets the fake clock run with real time after the load. */
async function open(page, c, { time, path = "/", ticks = false, wire = "wire-w", passphrase = "localtest" } = {}) {
  if (wire !== null) await serveWire(page, typeof wire === "function" ? wire : wireOf(wire));
  if (time) {
    if (ticks) await page.clock.install({ time: new Date(time) });
    else await page.clock.setFixedTime(new Date(time));
  }
  await page.addInitScript(
    ({ theme, passphrase }) => {
      localStorage.setItem("cpc.theme", theme);
      if (passphrase) localStorage.setItem("cpc.passphrase", passphrase);
      localStorage.setItem("cpc.your-team", "6");
      localStorage.setItem("cpc.announcement.season-sim-2026", "seen");
      localStorage.setItem("cpc.tour-seen", "1");
    },
    { theme: c.theme, passphrase },
  );
  await page.goto(`${SITE}${path}`);
  await page.locator("header").first().waitFor();
  await page.waitForTimeout(600);
}

const banner = (page) => page.locator("[data-deadline-banner]");

async function openSheet(page) {
  await page.locator("[data-deadline-countdown], [data-deadline-banner] button").first().click();
  await page.locator("[data-wire-sheet]").waitFor();
  await page.waitForTimeout(900);
}

/* The fit of the banner: the sideways scroll, the band row, and the banner box. */
async function fit(page) {
  return page.evaluate(() => {
    const header = document.querySelector("header");
    const strip = document.querySelector("[data-deadline-banner]");
    const row = header?.firstElementChild?.getBoundingClientRect();
    const box = strip?.getBoundingClientRect();
    const overlap = !!(row && box && box.top < row.bottom - 0.5);
    return {
      viewport: [window.innerWidth, window.innerHeight],
      sidewaysScroll: document.documentElement.scrollWidth - window.innerWidth,
      bandRowBottom: row?.bottom ?? null,
      bannerTop: box?.top ?? null,
      bannerBottom: box?.bottom ?? null,
      headerBottom: header?.getBoundingClientRect().bottom ?? null,
      bannerOverlapsBandRow: overlap,
      bannerPresent: !!strip,
    };
  });
}

/* The iPhone 15 check at 390 by 660 in WebKit, with the same opening as the test. */
async function iphone(browser, at, opts, after) {
  const context = await browser.newContext({ ...IPHONE, viewport: { width: 390, height: 660 } });
  const page = await context.newPage();
  await open(page, { width: 390, theme: "light" }, opts);
  if (after) await after(page);
  const result = await fit(page);
  writeFileSync(join(dir(at), "iphone-15-390x660.json"), JSON.stringify({ device: "iPhone 15 (WebKit) at 390x660", ...result }, null, 1));
  await context.close();
}

function want(at) {
  return ONLY.length === 0 || ONLY.includes(at);
}

/* ---------- phase off: the shipped config of cpc ---------- */
test.describe("off", () => {
  test.skip(PHASE !== "off", "phase off");

  test("AT-1", async ({ browser }) => {
    test.skip(!want("AT-1"));
    fresh("AT-1", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      await open(page, c, { time: OPEN });
      note("AT-1", "measure.jsonl", { ...c, eyebrow: await banner(page).locator("[data-deadline-eyebrow]").innerText(), countdown: await banner(page).locator("[data-deadline-countdown]").innerText(), ...(await fit(page)) });
      await page.screenshot({ path: shotPath("AT-1", "", c) });
      await page.context().close();
    }
    await iphone(browser, "AT-1", { time: OPEN });
  });

  test("AT-2", async ({ browser }) => {
    test.skip(!want("AT-2"));
    fresh("AT-2", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      await open(page, c, { time: OPEN, ticks: true });
      const before = await banner(page).locator("[data-deadline-countdown]").innerText();
      await page.clock.runFor(60_000);
      await page.waitForTimeout(300);
      const after = await banner(page).locator("[data-deadline-countdown]").innerText();
      note("AT-2", "measure.jsonl", { ...c, before, clockMovedMs: 60000, after });
      await page.screenshot({ path: shotPath("AT-2", "after", c) });
      await page.context().close();
    }
    await iphone(browser, "AT-2", { time: OPEN });
  });

  test("AT-3", async ({ browser }) => {
    test.skip(!want("AT-3"));
    fresh("AT-3", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      await open(page, c, { time: LAST_HOURS });
      const fill = await page.evaluate(() => {
        const probe = document.createElement("div");
        probe.style.background = "var(--color-accent)";
        document.body.append(probe);
        const accent = getComputedStyle(probe).backgroundColor;
        probe.remove();
        const b = document.querySelector("[data-deadline-banner] button");
        return { accentToken: accent, bannerBackground: getComputedStyle(b).backgroundColor, phase: document.querySelector("[data-deadline-banner]").getAttribute("data-phase") };
      });
      note("AT-3", "measure.jsonl", { ...c, countdown: await banner(page).locator("[data-deadline-countdown]").innerText(), ...fill });
      await page.screenshot({ path: shotPath("AT-3", "", c) });
      await page.context().close();
    }
    await iphone(browser, "AT-3", { time: LAST_HOURS });
  });

  test("AT-4", async ({ browser }) => {
    test.skip(!want("AT-4"));
    fresh("AT-4", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c, { reducedMotion: "reduce" });
      await open(page, c, { time: LAST_HOURS });
      const anims = await banner(page).evaluate((el) =>
        el.getAnimations({ subtree: true }).map((a) => ({ name: a.animationName ?? a.constructor.name, playState: a.playState })),
      );
      const reduce = await page.evaluate(() => matchMedia("(prefers-reduced-motion: reduce)").matches);
      note("AT-4", "measure.jsonl", { ...c, prefersReducedMotion: reduce, animationsInBanner: anims, running: anims.filter((a) => a.playState === "running").length });
      await page.screenshot({ path: shotPath("AT-4", "", c) });
      await page.context().close();
    }
    await iphone(browser, "AT-4", { time: LAST_HOURS });
  });

  test("AT-5", async ({ browser }) => {
    test.skip(!want("AT-5"));
    fresh("AT-5", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      await open(page, c, { time: OPEN, path: "/rankings/" });
      await expect(banner(page).locator("[data-deadline-badge]")).toBeVisible();
      const aria = await banner(page).ariaSnapshot();
      const role = await banner(page).locator("button, [role=button]").evaluateAll((els) => els.map((el) => ({ tag: el.tagName, role: el.getAttribute("role"), ariaLabel: el.getAttribute("aria-label"), haspopup: el.getAttribute("aria-haspopup") })));
      await page.locator("[data-deadline-countdown]").click();
      await page.locator("[data-wire-sheet]").waitFor();
      await page.waitForTimeout(900);
      note("AT-5", "measure.jsonl", { ...c, path: "/rankings/", bannerAriaSnapshot: aria, buttonsInBanner: role, tapped: "[data-deadline-countdown]", sheetOpen: await page.locator("[data-wire-sheet]").isVisible(), sheetDialogName: await page.getByRole("dialog").first().getAttribute("aria-labelledby") });
      await page.screenshot({ path: shotPath("AT-5", "", c) });
      await page.context().close();
    }
    await iphone(browser, "AT-5", { time: OPEN, path: "/rankings/" });
  });

  test("AT-6", async ({ browser }) => {
    test.skip(!want("AT-6"));
    fresh("AT-6", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      // The real Trade Wire route of the local API, with the real week 11 of cpc.
      const answer = page.waitForResponse((r) => /\/deadline\/trades/.test(r.url()) && r.request().method() === "GET");
      await open(page, c, { time: OPEN, wire: null });
      const response = await answer;
      const body = await response.json();
      await page.waitForTimeout(500);
      const badge = await banner(page).locator("[data-deadline-badge]").count();
      note("AT-6", "measure.jsonl", { ...c, routeUrl: response.url(), routeStatus: response.status(), routeLeg: body.leg, routeTradeCount: body.trades.length, badgeElements: badge, badgeText: badge ? await banner(page).locator("[data-deadline-badge]").innerText() : null, bannerAriaSnapshot: await banner(page).ariaSnapshot() });
      await page.screenshot({ path: shotPath("AT-6", "", c) });
      await page.context().close();
    }
    await iphone(browser, "AT-6", { time: OPEN, wire: null });
  });

  test("AT-7", async ({ browser }) => {
    test.skip(!want("AT-7"));
    fresh("AT-7", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      await open(page, c, { time: OPEN });
      const box = await banner(page).locator("button").first().boundingBox();
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      const rest = await page.locator("[data-deadline-grid]").evaluate((el) => ({ scale: getComputedStyle(el).scale, transform: getComputedStyle(el).transform }));
      await page.mouse.down();
      await page.waitForTimeout(400);
      const press = await page.locator("[data-deadline-grid]").evaluate((el) => {
        const s = getComputedStyle(el);
        return { scale: s.scale, transform: s.transform, transitionProperty: s.transitionProperty, transitionDuration: s.transitionDuration, transitionTimingFunction: s.transitionTimingFunction };
      });
      await page.screenshot({ path: shotPath("AT-7", "press", c) });
      await page.mouse.up();
      note("AT-7", "measure.jsonl", { ...c, atRest: rest, duringPress400ms: press });
      await page.context().close();
    }
    await iphone(browser, "AT-7", { time: OPEN });
  });

  test("AT-8", async ({ browser }) => {
    test.skip(!want("AT-8"));
    fresh("AT-8", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      await open(page, c, { time: OPEN });
      const m = await page.evaluate(() => {
        const r = (s) => document.querySelector(s).getBoundingClientRect();
        const btn = document.querySelector("[data-deadline-banner] button");
        const b = r("[data-deadline-banner] button");
        const e = r("[data-deadline-eyebrow]");
        const k = r("[data-deadline-countdown]");
        const border = parseFloat(getComputedStyle(btn).borderTopWidth);
        return { topPadding: +(e.top - b.top - border).toFixed(2), bottomPadding: +(b.bottom - k.bottom - parseFloat(getComputedStyle(btn).borderBottomWidth)).toFixed(2), eyebrowX: +e.left.toFixed(2), countdownX: +k.left.toFixed(2) };
      });
      note("AT-8", "measure.jsonl", { ...c, ...m, paddingDiff: +Math.abs(m.topPadding - m.bottomPadding).toFixed(2), xDiff: +Math.abs(m.eyebrowX - m.countdownX).toFixed(2) });
      await page.screenshot({ path: shotPath("AT-8", "", c) });
      await page.context().close();
    }
    await iphone(browser, "AT-8", { time: OPEN });
  });

  test("AT-9", async ({ browser }) => {
    test.skip(!want("AT-9"));
    fresh("AT-9", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      await open(page, c, { time: CLOSED });
      note("AT-9", "measure.jsonl", { ...c, bannerText: await banner(page).innerText(), badge: (await banner(page).locator("[data-deadline-badge]").count()) ? await banner(page).locator("[data-deadline-badge]").innerText() : null, bannerAriaSnapshot: await banner(page).ariaSnapshot() });
      await page.screenshot({ path: shotPath("AT-9", "", c) });
      await page.context().close();
    }
    await iphone(browser, "AT-9", { time: CLOSED });
  });

  test("AT-10", async ({ browser }) => {
    test.skip(!want("AT-10"));
    fresh("AT-10", "measure.jsonl");
    for (const c of COMBOS) {
      for (const [name, path] of [["front-door", "/"], ["analyzer", "/analyze/"]]) {
        const page = await newPage(browser, c);
        await open(page, c, { time: ENDED, path });
        await page.waitForTimeout(800);
        const eyebrow = await page.locator("[data-hero-slot=eyebrow]").allInnerTexts();
        note("AT-10", "measure.jsonl", { ...c, page: path, bannerCount: await banner(page).count(), heroEyebrows: eyebrow, textHasTradeDeadline: /trade deadline/i.test(await page.locator("body").innerText()) });
        await page.screenshot({ path: shotPath("AT-10", name, c) });
        await page.context().close();
      }
    }
    await iphone(browser, "AT-10", { time: ENDED });
  });

  test("AT-12", async ({ browser }) => {
    test.skip(!want("AT-12"));
    test.setTimeout(600_000);
    fresh("AT-12", "search.txt");
    const BANNED = /Lock|Rosters are locked|Deadline Board|feed|Jev|Advisor|Finder|Brian/g;
    for (const [tname, time] of [["open", OPEN], ["last-hours", LAST_HOURS], ["closed", CLOSED]]) {
      for (const [pname, path, sheet] of [["front-door", "/", false], ["sheet", "/", true], ["analyzer", "/analyze/", false]]) {
        for (const c of COMBOS) {
          const page = await newPage(browser, c);
          await open(page, c, { time, path });
          if (sheet) await openSheet(page);
          await page.waitForTimeout(500);
          if (c.width === 375 && c.theme === "light") {
            const dump = await page.evaluate(() => {
              const names = [...document.querySelectorAll("[aria-label],[alt],[title],[placeholder]")].map((el) => ["aria-label", "alt", "title", "placeholder"].map((a) => el.getAttribute(a)).filter(Boolean).join(" | "));
              return `--- visible text (body.innerText) ---\n${document.body.innerText}\n--- accessible names (aria-label, alt, title, placeholder) ---\n${names.join("\n")}`;
            });
            const file = `text-${pname}-${tname}.txt`;
            writeFileSync(join(dir("AT-12"), file), dump);
            const hits = [...dump.matchAll(BANNED)].map((m) => `${m[0]} in "...${dump.slice(Math.max(0, m.index - 30), m.index + 30).replace(/\n/g, " ")}..."`);
            note("AT-12", "search.txt", `${file}: ${hits.length} hits${hits.length ? `\n  ${hits.join("\n  ")}` : ""}`);
          }
          await page.screenshot({ path: shotPath("AT-12", `${pname}-${tname}`, c) });
          await page.context().close();
        }
      }
    }
  });

  test("AT-23 and AT-24 and AT-27", async ({ browser }) => {
    test.skip(!want("AT-23") && !want("AT-24") && !want("AT-27"));
    for (const at of ["AT-23", "AT-24", "AT-27"]) if (want(at)) fresh(at, "measure.jsonl");
    for (const c of COMBOS) {
      for (const [at, time, wire] of [["AT-23", OPEN, "wire-empty"], ["AT-24", CLOSED, "wire-empty"], ["AT-27", OPEN, "wire-w"]]) {
        if (!want(at)) continue;
        const page = await newPage(browser, c);
        await open(page, c, { time, wire });
        await openSheet(page);
        const sheet = page.locator("[data-wire-sheet]");
        note(at, "measure.jsonl", { ...c, emptyLine: (await sheet.locator("[data-wire-empty]").count()) ? await sheet.locator("[data-wire-empty]").innerText() : null, links: await sheet.locator("a").allInnerTexts() });
        await page.screenshot({ path: shotPath(at, "", c) });
        await page.context().close();
      }
    }
    if (want("AT-23")) await iphone(browser, "AT-23", { time: OPEN, wire: "wire-empty" }, openSheet);
    if (want("AT-24")) await iphone(browser, "AT-24", { time: CLOSED, wire: "wire-empty" }, openSheet);
    if (want("AT-27")) await iphone(browser, "AT-27", { time: OPEN }, openSheet);
  });

  test("AT-19", async ({ browser }) => {
    test.skip(!want("AT-19"));
    fresh("AT-19", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      await open(page, c, { time: OPEN, wire: "wire-two" });
      await openSheet(page);
      await page.locator(`[data-trade="${OTHER}"]`).waitFor();
      const gaps = await page.evaluate(() => {
        const trades = [...document.querySelectorAll("[data-wire-sheet] [data-trade]")];
        const lines = trades.map((t) => [...t.querySelectorAll("[data-wire-line]")].map((l) => l.getBoundingClientRect()));
        const inside = lines.map((ls) => ls.slice(1).map((l, i) => +(l.top - ls[i].bottom).toFixed(2)));
        const between = lines.slice(1).map((ls, i) => +(ls[0].top - lines[i][lines[i].length - 1].bottom).toFixed(2));
        // The gap above the first trade: from the rule on top of the list to its first line.
        const list = document.querySelector("[data-wire-sheet] ol").getBoundingClientRect();
        const ruleToFirst = +(lines[0][0].top - list.top - parseFloat(getComputedStyle(document.querySelector("[data-wire-sheet] ol")).borderTopWidth)).toFixed(2);
        return { trades: trades.map((t) => t.getAttribute("data-trade")), insideGaps: inside, betweenTrades: between, listRuleToFirstLine: ruleToFirst, liPadding: trades.map((t) => [getComputedStyle(t).paddingTop, getComputedStyle(t).paddingBottom, getComputedStyle(t).borderBottomWidth]) };
      });
      note("AT-19", "measure.jsonl", { ...c, ...gaps });
      await page.screenshot({ path: shotPath("AT-19", "", c) });
      await page.context().close();
    }
    await iphone(browser, "AT-19", { time: OPEN, wire: "wire-two" }, openSheet);
  });

  test("AT-20", async ({ browser }) => {
    test.skip(!want("AT-20"));
    test.setTimeout(400_000);
    fresh("AT-20", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      let serve = "wire-other";
      const log = [];
      await serveWire(page, () => ({ status: 200, body: fixture(serve) }), log);
      await open(page, c, { time: OPEN, ticks: true, wire: null });
      await page.clock.resume();
      await openSheet(page);
      await page.locator(`[data-trade="${OTHER}"]`).waitFor();
      const badgeBefore = await banner(page).locator("[data-deadline-badge]").innerText();
      await page.screenshot({ path: shotPath("AT-20", "before", c) });
      serve = "wire-two";
      const switched = Date.now();
      await page.waitForFunction((id) => !!document.querySelector(`[data-trade="${id}"]`), TRADE_W, { polling: "raf", timeout: 20_000 });
      const firstFrame = Date.now();
      const order = await page.locator("[data-wire-sheet] [data-trade]").evaluateAll((els) => els.map((e) => e.getAttribute("data-trade")));
      const badgeAfter = await banner(page).locator("[data-deadline-badge]").innerText();
      await page.waitForTimeout(700);
      await page.screenshot({ path: shotPath("AT-20", "after", c) });
      note("AT-20", "measure.jsonl", { ...c, routeChangeAt: new Date(switched).toISOString(), firstFrameOfTradeWAt: new Date(firstFrame).toISOString(), secondsToShow: +((firstFrame - switched) / 1000).toFixed(2), orderAfter: order, badgeBefore, badgeAfter, routeCalls: log });
      await page.context().close();
    }
    await iphone(browser, "AT-20", { time: OPEN, wire: "wire-two" }, openSheet);
  });

  test("AT-21", async ({ browser }) => {
    test.skip(!want("AT-21"));
    fresh("AT-21", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      const log = await serveWire(page, wireOf("wire-w"));
      await open(page, c, { time: OPEN, ticks: true, wire: null });
      await page.clock.resume();
      await openSheet(page);
      const updated = page.locator("[data-wire-updated]");
      await updated.waitFor();
      // Sample the live line every 100 ms in the page across the next poll, with the page clock (Date.now) of each sample.
      const samples = await page.evaluate(async () => {
        const out = [];
        const el = () => document.querySelector("[data-wire-updated]");
        for (let i = 0; i < 160; i++) {
          out.push([Date.now(), el()?.textContent.trim() ?? null]);
          await new Promise((r) => setTimeout(r, 100));
        }
        return out;
      });
      // The read is the first sample of "Updated 0s ago" after a higher count. Each later text is timed from it.
      const reset = samples.findIndex((x, i) => i > 0 && /Updated 0s/.test(x[1]) && !/Updated 0s/.test(samples[i - 1][1]));
      const t0 = reset >= 0 ? samples[reset][0] : samples[0][0];
      const after = reset >= 0 ? samples.slice(reset) : samples;
      const firstOf = (n) => after.find((x) => x[1] === `Updated ${n}s ago`);
      const at3 = firstOf(3);
      note("AT-21", "measure.jsonl", { ...c, method: "page samples each 100 ms; times by the page clock from the first 0s sample after a poll", firstSampleOf: Object.fromEntries([0, 1, 2, 3, 4].map((n) => [`${n}s`, firstOf(n) ? +((firstOf(n)[0] - t0) / 1000).toFixed(2) : null])), textAt3_0s: (after.find((x) => x[0] - t0 >= 3000) ?? [null, null])[1], liveDot: await page.locator("[data-wire-sheet] .deadline-live").count() });
      await page.screenshot({ path: shotPath("AT-21", "", c) });
      await page.context().close();
    }
    await iphone(browser, "AT-21", { time: OPEN }, openSheet);
  });

  test("AT-22", async ({ browser }) => {
    test.skip(!want("AT-22"));
    test.setTimeout(200_000);
    const c = { width: 375, theme: "light" };
    const page = await newPage(browser, c);
    const log = await serveWire(page, wireOf("wire-w"));
    await open(page, c, { time: OPEN, ticks: true, wire: null });
    await page.clock.resume();
    await page.waitForTimeout(12_000);
    const hide = Date.now();
    await page.evaluate(() => {
      Object.defineProperty(document, "visibilityState", { configurable: true, get: () => "hidden" });
      Object.defineProperty(document, "hidden", { configurable: true, get: () => true });
      document.dispatchEvent(new Event("visibilitychange"));
    });
    await page.waitForTimeout(30_000);
    const show = Date.now();
    await page.evaluate(() => {
      Object.defineProperty(document, "visibilityState", { configurable: true, get: () => "visible" });
      Object.defineProperty(document, "hidden", { configurable: true, get: () => false });
      document.dispatchEvent(new Event("visibilitychange"));
    });
    await page.waitForTimeout(3000);
    const rows = log.map((l) => ({ ...l, secondsFromHide: +((l.ms - hide) / 1000).toFixed(2), phase: l.ms < hide ? "shown" : l.ms < show ? "hidden" : "shown again", secondsAfterShow: l.ms >= show ? +((l.ms - show) / 1000).toFixed(2) : null }));
    writeFileSync(join(dir("AT-22"), "network-log.json"), JSON.stringify({ method: "Playwright route log of every GET of the Trade Wire route; the tab hides by document.visibilityState and a visibilitychange event", hideAt: new Date(hide).toISOString(), showAt: new Date(show).toISOString(), calls: rows }, null, 1));
    await page.context().close();
  });

  test("AT-25", async ({ browser }) => {
    test.skip(!want("AT-25"));
    test.setTimeout(400_000);
    fresh("AT-25", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      let fail = false;
      const log = await serveWire(page, () => (fail ? { status: 500, body: { detail: "error" } } : { status: 200, body: fixture("wire-w") }));
      await open(page, c, { time: OPEN, ticks: true, wire: null });
      await page.clock.resume();
      await openSheet(page);
      await page.locator(`[data-trade="${TRADE_W}"]`).waitFor();
      fail = true;
      await page.getByText("The last update failed.").waitFor({ timeout: 20_000 });
      await page.waitForTimeout(300);
      note("AT-25", "measure.jsonl", { ...c, tradeWStays: await page.locator(`[data-trade="${TRADE_W}"]`).isVisible(), note: await page.getByText("The last update failed.").innerText(), routeCalls: log });
      await page.screenshot({ path: shotPath("AT-25", "", c) });
      await page.context().close();
    }
  });

  test("AT-30", async ({ browser }) => {
    test.skip(!want("AT-30"));
    fresh("AT-30", "measure.jsonl");
    for (const c of COMBOS) {
      for (const sheetName of ["trade-wire", "team-sheet"]) {
        const page = await newPage(browser, c);
        await open(page, c, { time: OPEN });
        let content;
        if (sheetName === "trade-wire") {
          await openSheet(page);
          content = page.locator("[data-wire-sheet]");
        } else {
          await page.locator('button[aria-label^="Your team"]').first().click();
          await page.waitForTimeout(900);
          content = page.locator('[role=dialog]:has([data-slot="sheet-grip"])').last();
        }
        const grip = content.locator('[data-slot="sheet-grip"]').first();
        const g = await grip.boundingBox();
        const measure = () => content.evaluate((el) => {
          const r = el.getBoundingClientRect();
          const after = getComputedStyle(el, "::after");
          const afterHeight = parseFloat(after.height) || 0;
          return { boxTop: +r.top.toFixed(1), boxBottom: +r.bottom.toFixed(1), bleedHeight: afterHeight, bleedBackground: after.backgroundColor, boxBackground: getComputedStyle(el).backgroundColor, surfaceBottom: +(r.bottom + afterHeight).toFixed(1), viewportBottom: window.innerHeight };
        });
        const before = await measure();
        await page.mouse.move(g.x + g.width / 2, g.y + g.height / 2);
        await page.mouse.down();
        const samples = [];
        for (let i = 1; i <= 10; i++) {
          await page.mouse.move(g.x + g.width / 2, g.y + g.height / 2 - 20 * i);
          await page.waitForTimeout(30);
          samples.push({ dragged: 20 * i, ...(await measure()) });
        }
        await page.waitForTimeout(150);
        const during = await measure();
        await page.screenshot({ path: shotPath("AT-30", `${sheetName}-drag`, c) });
        await page.mouse.up();
        note("AT-30", "measure.jsonl", { ...c, sheet: sheetName, beforeDrag: before, during200pxDrag: during, visibleSurfaceGapAtBottom: +(during.viewportBottom - Math.min(during.viewportBottom, during.surfaceBottom)).toFixed(1), boxGapAtBottom: +(during.viewportBottom - during.boxBottom).toFixed(1), samples });
        await page.context().close();
      }
    }
  });

  test("AT-34", async ({ browser }) => {
    test.skip(!want("AT-34"));
    fresh("AT-34", "measure.jsonl");
    for (const c of COMBOS) {
      for (const [name, time] of [["open", OPEN], ["closed", CLOSED]]) {
        const page = await newPage(browser, c);
        await open(page, c, { time, path: "/analyze/" });
        await page.waitForTimeout(800);
        note("AT-34", "measure.jsonl", { ...c, time, heroEyebrows: await page.locator("main [data-hero-slot=eyebrow]").allInnerTexts() });
        await page.screenshot({ path: shotPath("AT-34", name, c) });
        await page.context().close();
      }
    }
    await iphone(browser, "AT-34", { time: OPEN, path: "/analyze/" });
  });

  test("AT-52", async ({ request }) => {
    test.skip(!want("AT-52"));
    const lines = [];
    for (const path of ["/deadline/", "/deadline-board/"]) {
      const r = await request.get(`${SITE}${path}`);
      lines.push(`GET ${path} -> ${r.status()}`);
    }
    writeFileSync(join(dir("AT-52"), "status.txt"), `${lines.join("\n")}\n`);
  });
});

/* AT-26 runs on the shipped build and on the build with the finder flag on. */
test("AT-26", async ({ browser }) => {
  test.skip(!want("AT-26") || !["off", "on"].includes(PHASE));
  const flag = PHASE === "on" ? "flag-on" : "flag-off";
  fresh("AT-26", `measure-${flag}.jsonl`);
  for (const c of COMBOS) {
    const page = await newPage(browser, c);
    await open(page, c, { time: OPEN });
    await openSheet(page);
    await page.locator("[data-wire-sheet] a", { hasText: "Grade a trade" }).click();
    await page.waitForURL(/analyze/);
    await page.locator('[aria-label="Mode"]').waitFor({ timeout: 5000 }).catch(() => undefined);
    await page.waitForTimeout(1200);
    const mode = await page.locator('[aria-label="Mode"]').count() ? await page.locator('[aria-label="Mode"]').ariaSnapshot() : "no Mode switch on the page";
    note("AT-26", `measure-${flag}.jsonl`, { ...c, finderFlag: flag, url: page.url(), modeSwitch: mode, heroTitle: await page.locator("[data-hero-slot=title]").first().innerText().catch(() => null) });
    await page.screenshot({ path: shotPath("AT-26", flag, c) });
    await page.context().close();
  }
});


/* ---------- phase norcal ---------- */
test.describe("norcal", () => {
  test.skip(PHASE !== "norcal", "phase norcal");
  test("AT-11", async ({ browser }) => {
    fresh("AT-11", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      await open(page, c, { time: OPEN });
      note("AT-11", "measure.jsonl", { ...c, bannerCount: await banner(page).count(), title: await page.title(), textHasTradeDeadline: /trade deadline/i.test(await page.locator("body").innerText()) });
      await page.screenshot({ path: shotPath("AT-11", "", c) });
      await page.context().close();
    }
    await iphone(browser, "AT-11", { time: OPEN });
  });
});

/* ---------- phase lock: the Lock 1 h after the fixed clock, in a local build only ---------- */
test.describe("lock", () => {
  test.skip(PHASE !== "lock", "phase lock");
  test("AT-50", async ({ browser }) => {
    fresh("AT-50", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      await open(page, c, { time: OPEN });
      note("AT-50", "measure.jsonl", { ...c, clock: OPEN, phase: await banner(page).getAttribute("data-phase"), countdown: await banner(page).locator("[data-deadline-countdown]").innerText() });
      await page.screenshot({ path: shotPath("AT-50", "", c) });
      await page.context().close();
    }
    await iphone(browser, "AT-50", { time: OPEN });
  });
});

/* ---------- phase on: the finder flag on, in a local build only ---------- */
const HELD = new Set();
async function holdFind(page, onBody) {
  await page.route(/\/find-stream/, async (route) => {
    if (route.request().method() === "OPTIONS") return route.fulfill({ status: 204, headers: CORS });
    onBody?.(route.request().postData());
    HELD.add(route); // never answered, so the wait goes on
  });
}
const modeItem = (page, label) => page.locator('[aria-label="Mode"]').getByText(label, { exact: true });

async function findReady(page) {
  await page.getByRole("button", { name: "Find a Trade" }).waitFor({ timeout: 30_000 });
  await expect(page.getByRole("button", { name: "Find a Trade" })).toBeEnabled({ timeout: 30_000 });
}

test.describe("on", () => {
  test.skip(PHASE !== "on", "phase on");

  test("AT-18", async ({ browser }) => {
    test.skip(!want("AT-18"));
    fresh("AT-18", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      await open(page, c, { time: OPEN });
      await openSheet(page);
      await page.locator(`[data-trade="${TRADE_W}"]`).waitFor();
      const order = await page.evaluate((w) => {
        const sheet = document.querySelector("[data-wire-sheet]");
        const find = (pred) => [...sheet.querySelectorAll("*")].find(pred);
        const parts = {
          "Grade a trade": find((el) => el.tagName === "A" && el.textContent.trim() === "Grade a trade"),
          "Find a trade": find((el) => el.tagName === "A" && el.textContent.trim() === "Find a trade"),
          eyebrow: find((el) => el.children.length === 0 && /^Trade deadline/i.test(el.textContent.trim())),
          "Trade Wire": find((el) => el.children.length === 0 && el.textContent.trim() === "Trade Wire"),
          "live dot + Updated": sheet.querySelector("[data-wire-updated]"),
          "trade W": sheet.querySelector(`[data-trade="${w}"]`),
        };
        const all = [...sheet.querySelectorAll("*")];
        return Object.entries(parts).map(([name, el]) => ({ name, domIndex: el ? all.indexOf(el) : null, top: el ? +el.getBoundingClientRect().top.toFixed(1) : null, left: el ? +el.getBoundingClientRect().left.toFixed(1) : null, text: el ? el.innerText.replace(/\s+/g, " ").slice(0, 80) : null }));
      }, TRADE_W);
      note("AT-18", "measure.jsonl", { ...c, partsInOrder: order });
      await page.screenshot({ path: shotPath("AT-18", "", c) });
      await page.context().close();
    }
    await iphone(browser, "AT-18", { time: OPEN }, openSheet);
  });

  test("AT-28 and AT-29", async ({ browser }) => {
    test.skip(!want("AT-28") && !want("AT-29"));
    if (want("AT-28")) fresh("AT-28", "measure.jsonl");
    if (want("AT-29")) fresh("AT-29", "measure.jsonl");
    for (const c of COMBOS) {
      if (want("AT-28")) {
        const page = await newPage(browser, c);
        await open(page, c, { time: OPEN });
        await openSheet(page);
        await page.locator("[data-wire-sheet] a", { hasText: "Find a trade" }).click();
        await page.waitForURL(/analyze/);
        await findReady(page).catch(() => undefined);
        await page.waitForTimeout(1000);
        note("AT-28", "measure.jsonl", { ...c, url: page.url(), modeSwitch: await page.locator('[aria-label="Mode"]').ariaSnapshot(), heroTitle: await page.locator("main [data-hero-slot=title]").first().innerText().catch(() => null), heroText: (await page.locator('section[aria-label="Trade Ideas"].bg-band').innerText().catch(() => "")).slice(0, 400) });
        await page.screenshot({ path: shotPath("AT-28", "", c) });
        await page.context().close();
      }
      if (want("AT-29")) {
        const page = await newPage(browser, c);
        await open(page, c, { time: CLOSED });
        await openSheet(page);
        note("AT-29", "measure.jsonl", { ...c, linksInSheet: await page.locator("[data-wire-sheet] a").allInnerTexts() });
        await page.screenshot({ path: shotPath("AT-29", "", c) });
        await page.context().close();
      }
    }
    if (want("AT-29")) await iphone(browser, "AT-29", { time: CLOSED }, openSheet);
  });

  test("AT-31 and AT-33 and AT-53", async ({ browser }) => {
    test.skip(!want("AT-31") && !want("AT-33") && !want("AT-53"));
    for (const at of ["AT-31", "AT-33", "AT-53"]) if (want(at)) fresh(at, "measure.jsonl");
    for (const c of COMBOS) {
      if (want("AT-31")) {
        const page = await newPage(browser, c);
        await open(page, c, { time: OPEN, path: "/analyze/" });
        await page.locator('[aria-label="Mode"]').waitFor();
        await page.waitForTimeout(800);
        const m = await page.locator('[aria-label="Mode"]').evaluate((root) => {
          const items = [...root.querySelectorAll("*")].filter((el) => ["Grade a trade", "Find a trade"].includes(el.textContent.trim()) && el.children.length === 0).map((el) => el.closest("button,[role=radio],[role=tab]") ?? el);
          const hero = root.closest("section");
          const hr = hero.getBoundingClientRect();
          const rr = root.getBoundingClientRect();
          const cs = getComputedStyle(hero);
          return { heroWidth: +hr.width.toFixed(2), heroInner: [+(hr.left + parseFloat(cs.paddingLeft)).toFixed(2), +(hr.right - parseFloat(cs.paddingRight)).toFixed(2)], switchLeftRight: [+rr.left.toFixed(2), +rr.right.toFixed(2)], switchWidth: +rr.width.toFixed(2), halves: items.map((el) => ({ text: el.textContent.trim(), role: el.getAttribute("role"), width: +el.getBoundingClientRect().width.toFixed(2), left: +el.getBoundingClientRect().left.toFixed(2) })), rootRole: root.getAttribute("role") };
        });
        note("AT-31", "measure.jsonl", { ...c, ...m, halfWidthDiff: m.halves.length === 2 ? +Math.abs(m.halves[0].width - m.halves[1].width).toFixed(2) : null });
        await page.screenshot({ path: shotPath("AT-31", "", c) });
        await page.context().close();
      }
      for (const at of ["AT-33", "AT-53"]) {
        if (!want(at)) continue;
        const page = await newPage(browser, c);
        await open(page, c, { time: OPEN, path: "/analyze/?mode=find" });
        await findReady(page);
        await page.waitForTimeout(800);
        const hero = page.locator('section[aria-label="Trade Ideas"].bg-band');
        const text = await hero.innerText();
        note(at, "measure.jsonl", { ...c, heroText: text, positionChips: await page.locator('[aria-label="Position"]').innerText().catch(() => null), teamCountChoice: /\b(two|three|2|3) teams?\b/i.test(text) });
        await page.screenshot({ path: shotPath(at, "", c) });
        await page.context().close();
      }
    }
    if (want("AT-31")) await iphone(browser, "AT-31", { time: OPEN, path: "/analyze/" });
  });

  test("AT-32", async ({ browser }) => {
    test.skip(!want("AT-32"));
    fresh("AT-32", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      await holdFind(page);
      await open(page, c, { time: OPEN, path: "/analyze/?mode=find" });
      await findReady(page);
      await page.getByRole("button", { name: "Find a Trade" }).click();
      await page.locator('section[aria-label="Finding Trades"]').waitFor();
      await page.waitForTimeout(600);
      const grade = modeItem(page, "Grade a trade");
      const gb = await grade.boundingBox();
      await page.mouse.click(gb.x + gb.width / 2, gb.y + gb.height / 2);
      await page.waitForTimeout(800);
      const state = await page.locator('[aria-label="Mode"]').evaluate((root) => ({
        root: Object.fromEntries([...root.attributes].map((a) => [a.name, a.value]).filter(([n]) => n !== "class" && n !== "style")),
        items: [...root.querySelectorAll("button,[role=radio]")].map((el) => ({ text: el.textContent.trim(), attrs: Object.fromEntries([...el.attributes].map((a) => [a.name, a.value]).filter(([n]) => n !== "class" && n !== "style")) })),
      }));
      note("AT-32", "measure.jsonl", { ...c, url: page.url(), waitStillShows: await page.locator('section[aria-label="Finding Trades"]').isVisible(), switchAfterTapOnGrade: state });
      await page.screenshot({ path: shotPath("AT-32", "", c) });
      await page.context().close();
    }
  });

  test("AT-35", async ({ browser }) => {
    test.skip(!want("AT-35"));
    fresh("AT-35", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      let body = null;
      await holdFind(page, (b) => (body = b));
      await open(page, c, { time: OPEN, path: "/analyze/?mode=find" });
      await findReady(page);
      await page.locator('[aria-label="Position"]').getByText("RB", { exact: true }).click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: shotPath("AT-35", "rb", c) });
      await page.getByRole("button", { name: "Find a Trade" }).click();
      await expect.poll(() => body, { timeout: 10_000 }).not.toBeNull();
      note("AT-35", "measure.jsonl", { ...c, analyzerFindRequestBody: JSON.parse(body) });
      await page.context().close();
    }
  });

  test("AT-40", async ({ browser }) => {
    test.skip(!want("AT-40"));
    fresh("AT-40", "measure.jsonl");
    for (const c of COMBOS) {
      const page = await newPage(browser, c);
      await page.route(/\/find-stream/, (route) => (route.request().method() === "OPTIONS" ? route.fulfill({ status: 204, headers: CORS }) : route.fulfill({ status: 500, headers: CORS, contentType: "application/json", body: JSON.stringify({ detail: "error" }) })));
      await open(page, c, { time: OPEN, path: "/analyze/?mode=find" });
      await findReady(page);
      await page.getByRole("button", { name: "Find a Trade" }).click();
      await page.getByRole("button", { name: "Try Again" }).waitFor({ timeout: 20_000 });
      await page.waitForTimeout(500);
      note("AT-40", "measure.jsonl", { ...c, heroText: await page.locator('section[aria-label="Trade Ideas"].bg-band').innerText() });
      await page.screenshot({ path: shotPath("AT-40", "", c) });
      await page.context().close();
    }
  });

  test("AT-12 find mode", async ({ browser }) => {
    test.skip(!want("AT-12"));
    const BANNED = /Lock|Rosters are locked|Deadline Board|feed|Jev|Advisor|Finder|Brian/g;
    for (const [tname, time] of [["open", OPEN], ["last-hours", LAST_HOURS], ["closed", CLOSED]]) {
      for (const [pname, path, sheet] of [["analyzer-find-flag-on", "/analyze/?mode=find", false], ["sheet-find-flag-on", "/", true]]) {
        const c = { width: 375, theme: "light" };
        const page = await newPage(browser, c);
        await open(page, c, { time, path });
        if (sheet) await openSheet(page);
        await page.waitForTimeout(1200);
        const dump = await page.evaluate(() => {
          const names = [...document.querySelectorAll("[aria-label],[alt],[title],[placeholder]")].map((el) => ["aria-label", "alt", "title", "placeholder"].map((a) => el.getAttribute(a)).filter(Boolean).join(" | "));
          return `--- visible text (body.innerText) ---\n${document.body.innerText}\n--- accessible names (aria-label, alt, title, placeholder) ---\n${names.join("\n")}`;
        });
        const file = `text-${pname}-${tname}.txt`;
        writeFileSync(join(dir("AT-12"), file), dump);
        const hits = [...dump.matchAll(BANNED)].map((m) => `${m[0]} in "...${dump.slice(Math.max(0, m.index - 30), m.index + 30).replace(/\n/g, " ")}..."`);
        note("AT-12", "search.txt", `${file}: ${hits.length} hits${hits.length ? `\n  ${hits.join("\n  ")}` : ""}`);
        await page.screenshot({ path: shotPath("AT-12", `${pname}-${tname}`, c) });
        await page.context().close();
      }
    }
  });

  /* AT-36 to AT-39: one real press per size and theme against the local API, with the result cache emptied first. */
  test("AT-36 to AT-39", async ({ browser }) => {
    test.skip(!want("AT-36"));
    test.setTimeout(1_200_000);
    for (const at of ["AT-36", "AT-37", "AT-38", "AT-39"]) fresh(at, "measure.jsonl");
    for (const c of COMBOS) {
      for (const f of existsSync(join(CACHE, "cpc")) ? readdirSync(join(CACHE, "cpc")) : []) if (/^[0-9a-f]{64}\.json$/.test(f)) rmSync(join(CACHE, "cpc", f));
      const page = await newPage(browser, c);
      // The tee of the stream: a copy of each chunk of the find stream with its time, read beside the page.
      await page.addInitScript(() => {
        window.__chunks = [];
        window.__lines = [];
        const real = window.fetch;
        window.fetch = async (...args) => {
          const response = await real(...args);
          const url = String(args[0]?.url ?? args[0]);
          if (url.includes("/find-stream")) {
            const reader = response.clone().body.getReader();
            const dec = new TextDecoder();
            (async () => {
              for (;;) {
                const { done, value } = await reader.read();
                if (done) break;
                window.__chunks.push([Math.round(performance.now()), dec.decode(value)]);
              }
            })();
          }
          return response;
        };
        new MutationObserver(() => {
          const status = document.querySelector('section[aria-label="Finding Trades"] [role=status]');
          const text = status?.textContent ?? null;
          const last = window.__lines[window.__lines.length - 1];
          const lit = [...document.querySelectorAll("[data-team-read]")].filter((el) => el.getAttribute("data-lit") === "true").map((el) => el.getAttribute("data-team-read"));
          if (text !== null && (!last || last[1] !== text || last[2].length !== lit.length)) window.__lines.push([Math.round(performance.now()), text, lit]);
        }).observe(document, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ["data-lit"] });
      });
      const requests = [];
      page.on("request", (r) => requests.push({ ms: Date.now(), method: r.method(), url: r.url() }));
      await open(page, c, { path: "/analyze/?mode=find" });
      await findReady(page);
      const tap = await page.evaluate(() => Math.round(performance.now()));
      await page.getByRole("button", { name: "Find a Trade" }).click();
      const status = page.locator('section[aria-label="Finding Trades"] [role=status]');
      await status.waitFor();
      await page.waitForTimeout(400);
      await page.screenshot({ path: shotPath("AT-36", "line-1", c) });
      await page.waitForFunction(() => /^[3-5] of 5/.test(document.querySelector('section[aria-label="Finding Trades"] [role=status]')?.textContent ?? ""), null, { timeout: 60_000 });
      await page.waitForTimeout(300);
      await page.screenshot({ path: shotPath("AT-36", "line-2", c) });
      if (c.width === 375 && c.theme === "light") writeFileSync(join(dir("AT-36"), "stagelines-dom.html"), await page.locator('section[aria-label="Finding Trades"]').evaluate((el) => el.querySelector(".t-think")?.closest("[aria-hidden]")?.outerHTML ?? el.outerHTML));
      await page.screenshot({ path: shotPath("AT-37", "", c) });
      await page.locator('ol[aria-label="Trade ideas"]').or(page.getByText(/no trade/i)).first().waitFor({ timeout: 150_000 });
      await page.waitForTimeout(1500);
      const chunks = await page.evaluate(() => window.__chunks);
      const lines = await page.evaluate(() => window.__lines);
      writeFileSync(join(dir("AT-36"), `stream-${c.width}-${c.theme}.txt`), chunks.map(([t, s]) => s.split("\n").filter(Boolean).map((l) => `${((t - tap) / 1000).toFixed(2)} s  ${l}`).join("\n")).join("\n"));
      note("AT-36", "measure.jsonl", { ...c, tapAtMs: tap, lineTextWithSecondsFromTap: lines.map(([t, text]) => [+((t - tap) / 1000).toFixed(2), text]) });
      note("AT-37", "measure.jsonl", { ...c, litAvatarsWithSecondsFromTap: lines.filter((l, i) => i === 0 || l[2].length !== lines[i - 1][2].length).map(([t, , lit]) => [+((t - tap) / 1000).toFixed(2), lit]), teamPartsOfStreamInOrder: chunks.flatMap(([, s]) => [...s.matchAll(/"data-team", "data": \{"roster_id": (\d+)\}/g)].map((m) => m[1])) });
      const answer = chunks.map(([, s]) => s).join("").split("\n").find((l) => l.includes('"data-answer"'));
      if (answer) writeFileSync(join(dir("AT-38"), `find-answer-${c.width}-${c.theme}.json`), JSON.stringify(JSON.parse(answer.slice(6)).data.document, null, 1));
      const cards = page.locator('ol[aria-label="Trade ideas"] article');
      note("AT-38", "measure.jsonl", { ...c, cardCount: await cards.count(), cards: await cards.evaluateAll((els) => els.map((el) => ({ lean: el.querySelector("h3")?.textContent, caseLines: (() => { const p = el.querySelector("p.line-clamp-3"); if (!p) return null; const lh = parseFloat(getComputedStyle(p).lineHeight); return { text: p.textContent, renderedLines: Math.round(p.getBoundingClientRect().height / lh), clamp: getComputedStyle(p).webkitLineClamp }; })(), bulletsFolded: el.querySelector("[data-open]") === null && !!el.querySelector("button[aria-expanded=false]"), headings: [...el.querySelectorAll("h1,h2,h3,h4")].map((h) => h.textContent) }))) });
      await page.screenshot({ path: shotPath("AT-38", "", c), fullPage: true });
      const mark = requests.length;
      const clickAt = Date.now();
      const openButton = cards.first().getByRole("button", { name: "See the Full Result" });
      let tapError = null;
      const openState = await openButton.evaluate((el) => ({ disabled: el.disabled, ariaDisabled: el.getAttribute("aria-disabled"), text: el.textContent })).catch((e) => String(e).slice(0, 200));
      await openButton.click({ timeout: 15_000 }).catch((e) => (tapError = String(e).slice(0, 300)));
      await page.waitForTimeout(3000);
      const after = requests.slice(mark).filter((r) => !r.url.startsWith(SITE));
      note("AT-39", "measure.jsonl", { ...c, url: page.url(), apiRequestsAfterTap: after.map((r) => ({ ...r, msAfterTap: r.ms - clickAt })), analyzeRequests: after.filter((r) => /\/analyze(\?|$)/.test(new URL(r.url).pathname)).length, openButton: openState, tapError, modeSwitch: await page.locator('[aria-label="Mode"]').first().ariaSnapshot({ timeout: 5000 }).catch(() => null), heroTitles: await page.locator("main [data-hero-slot=title]").allInnerTexts() });
      await page.screenshot({ path: shotPath("AT-39", "", c), fullPage: true });
      await page.context().close();
    }
  });
});

/* ---------- phase at49: one fresh ask for trade ideas on the front door, against a freshly started local API ---------- */
test.describe("at49", () => {
  test.skip(PHASE !== "at49", "phase at49");
  test("AT-49 run", async ({ browser }) => {
    test.setTimeout(240_000);
    const run = process.env.RUN;
    const [width, theme] = (process.env.COMBO ?? "390-light").split("-");
    const c = { width: Number(width), theme };
    // A fresh context: no cookie, no session storage, no cache. The stored team and passphrase skip the two first-visit sheets.
    const context = await browser.newContext(c.width === 390 ? { ...IPHONE, viewport: { width: 390, height: 660 } } : { viewport: { width: c.width, height: 900 } });
    const page = await context.newPage();
    const requests = [];
    page.on("response", (r) => { if (!r.url().startsWith(SITE)) requests.push({ ms: Date.now(), status: r.status(), method: r.request().method(), url: r.url() }); });
    await open(page, c, { wire: null });
    await page.getByRole("button", { name: "More" }).click();
    await page.waitForTimeout(800);
    // The Topic button of Trade ideas: its name starts with the Topic name. A first tap on a row chip shows its fact
    // strip, and the strip button "Open Trade ideas" opens the Topic.
    const chip = page.getByRole("button", { name: /^Trade ideas/ }).first();
    const chipName = await chip.getAttribute("aria-label", { timeout: 10_000 }).catch(() => null) ?? (await chip.innerText({ timeout: 5000 }));
    const asked = Date.now();
    await chip.click({ timeout: 10_000 });
    await page.waitForTimeout(600);
    const strip = page.getByRole("button", { name: "Open Trade ideas" });
    if (await strip.isVisible().catch(() => false)) await strip.click();
    const retry = page.getByText("The question did not go through. Ask again.");
    const settled = page.locator('[role=article] [role=status]', { hasText: /Checked|Settled|Done/ });
    const cards = page.getByRole("article", { name: "Trade ideas" }).getByRole("region", { name: "Trade ideas" });
    // Poll both ends each 250 ms, so no long wait stays open after the answer.
    let outcome = "timeout";
    for (const until = Date.now() + 200_000; Date.now() < until; await page.waitForTimeout(250)) {
      if ((await retry.count()) > 0) { outcome = "retry line"; break; }
      if ((await cards.count()) > 0) { outcome = "trade ideas answer"; break; }
    }
    const answered = Date.now();
    console.log(`answered: ${outcome}`);
    await new Promise((done) => setTimeout(done, 2500));
    const result = { run, combo: process.env.COMBO, chip: chipName, askedAt: new Date(asked).toISOString(), secondsToAnswer: +((answered - asked) / 1000).toFixed(1), outcome, retryLineCount: await retry.count(), articleText: (await page.getByRole("article", { name: "Trade ideas" }).first().innerText({ timeout: 5000 }).catch(() => "")).slice(0, 1500), apiResponses: requests };
    writeFileSync(join(dir("AT-49"), `run-${run}.json`), JSON.stringify(result, null, 1));
    // The answer sits at the end of the Thread, so a viewport shot after a scroll to the end shows it.
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight)).catch(() => undefined);
    await page.waitForTimeout(500);
    const shot = process.env.COMBO !== "390-light" ? shotPath("AT-49", "answer", c) : join(dir("AT-49"), `run-${run}-390x660.png`);
    await page.screenshot({ path: shot, fullPage: true, timeout: 30_000 }).catch((e) => writeFileSync(`${shot}.error.txt`, String(e).slice(0, 300)));
    await context.close();
  });
});

/* ---------- AT-35, the front door side: the typed question "trade ideas for an RB", against the real local API ---------- */
test("AT-35 front door", async ({ browser }) => {
  test.skip(PHASE !== "off" || !want("AT-35fd"));
  test.setTimeout(240_000);
  const c = { width: 375, theme: "light" };
  const page = await newPage(browser, c);
  await page.addInitScript(() => {
    window.__chunks = [];
    const real = window.fetch;
    window.fetch = async (...args) => {
      const response = await real(...args);
      const url = String(args[0]?.url ?? args[0]);
      if (/trade-ideas|\/ask/.test(url) && response.body) {
        const reader = response.clone().body.getReader();
        const dec = new TextDecoder();
        (async () => { for (;;) { const { done, value } = await reader.read(); if (done) break; window.__chunks.push([url, dec.decode(value)]); } })();
      }
      return response;
    };
  });
  const posts = [];
  page.on("request", (r) => { if (r.method() === "POST" && !r.url().startsWith(SITE)) posts.push({ url: r.url(), body: r.postData() }); });
  await open(page, c, { wire: null });
  await page.getByRole("textbox", { name: /Ask a question/ }).fill("trade ideas for an RB");
  await page.getByRole("button", { name: "Send" }).click();
  await expect.poll(async () => (await page.evaluate(() => window.__chunks.map((x) => x[1]).join(""))).includes('"data-limit"'), { timeout: 120_000 }).toBe(true);
  const stream = await page.evaluate(() => window.__chunks.map((x) => x[1]).join(""));
  const limit = stream.split("\n").find((l) => l.includes('"data-limit"'));
  writeFileSync(join(dir("AT-35"), "front-door.json"), JSON.stringify({ typed: "trade ideas for an RB", postRequests: posts, limitPartOfStream: limit ? JSON.parse(limit.slice(6)) : null }, null, 1));
  await page.context().close();
});
