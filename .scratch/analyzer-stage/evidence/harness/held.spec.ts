/* The held-request tests of trade T, trade B, and trade L, and the idle tests: AT-1, 2, 4, 9, 15, 16, 27, 28, 33. */
import { test, expect, type Page } from "@playwright/test";
import { writeFileSync } from "node:fs";
import { openAnalyzer, serveDir, SCR, T_QUERY, HERO, WAIT_HERO, dir, log, reset, holdAnalyze, settle, newPage, startWait, waitState, untilElapsed, WIDTHS, THEMES } from "./lib";
const CMD = "EV_TESTS=<scratch>/pw2/tests pnpm exec playwright test --config pw-evidence.config.ts held  (see steps.txt)";
export const L_QUERY = "?team=2&with=11&give=8144&get=9502";
let srv: { close: () => Promise<void> };
test.beforeAll(async () => { srv = await serveDir(`${SCR}/r2-out-cpc`, 4173); });
test.afterAll(async () => { await srv.close(); });
const frames = (page: Page, sel: string) => page.locator(sel).evaluate((el) => Number((el as HTMLCanvasElement).dataset.meshFrames ?? 0));

test("AT-1 idle mesh", async ({ browser }) => {
  reset("AT-1", CMD);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { ctx, page } = await newPage(browser, width);
    await openAnalyzer(page, "", theme);
    await page.waitForTimeout(3000);
    await page.locator(HERO).screenshot({ path: `${dir("AT-1")}/${width}-${theme}.png` });
    if (width === 1280) {
      const f0 = await frames(page, `${HERO} canvas[data-hero-mesh]`);
      const a = await page.locator(HERO).screenshot({ path: `${dir("AT-1")}/a-1280-${theme}.png` });
      await page.waitForTimeout(2000);
      const b = await page.locator(HERO).screenshot({ path: `${dir("AT-1")}/b-1280-${theme}.png` });
      const f1 = await frames(page, `${HERO} canvas[data-hero-mesh]`);
      const pitch = await page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue("--hero-grid") || "n/a");
      log("AT-1", `1280 ${theme}: shots a and b 2 s apart are byte-equal: ${a.equals(b)}; the canvas drew ${f1 - f0} frames between them (data-mesh-frames ${f0} -> ${f1}); --hero-grid ${pitch}`);
      const stack = await page.locator("[data-stage-team]").count();
      log("AT-1", `1280 ${theme}: stage rows in the idle hero: ${stack}`);
    }
    await ctx.close();
  }
});

test("AT-2 add a player", async ({ browser }) => {
  reset("AT-2", CMD);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { ctx, page } = await newPage(browser, width);
    await openAnalyzer(page, "?team=6&with=12", theme);
    await settle(page);
    await page.locator(HERO).screenshot({ path: `${dir("AT-2")}/before-${width}-${theme}.png` });
    const before = await page.locator(`${HERO} [data-mesh-anchor]`).evaluateAll((els) => els.map((el) => el.textContent?.replace(/\s+/g, " ").trim()));
    log("AT-2", `${width} ${theme}: before the add, the stage rows read: ${before.length ? before.join(" | ") : "none"} (${before.length} rows); headshot tokens in the hero: ${await page.locator(`${HERO} [data-mesh-hole][title]`).count()}`);
    await page.getByRole("button", { name: "Add a player Team Two gets" }).click();
    const sheet = page.getByRole("dialog");
    await sheet.getByRole("tab", { name: "Bo Girds" }).click().catch(() => undefined);
    await sheet.getByRole("checkbox", { name: /Kenneth Walker III/ }).click();
    await sheet.getByRole("button", { name: /^Done/ }).click();
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await settle(page);
    await page.locator(HERO).screenshot({ path: `${dir("AT-2")}/after-${width}-${theme}.png` });
    const rows = await page.locator(`${HERO} [data-mesh-anchor]`).evaluateAll((els) => els.map((el) => el.textContent?.replace(/\s+/g, " ").trim()));
    const heads = await page.locator(`${HERO} [data-mesh-hole][title]`).count();
    log("AT-2", `${width} ${theme}: after the add, the stage rows read: ${rows.join(" | ")}; headshot tokens in the hero: ${heads}`);
    await ctx.close();
  }
});

test("AT-28 idle trade T", async ({ browser }) => {
  reset("AT-28", CMD);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { ctx, page } = await newPage(browser, width);
    await openAnalyzer(page, T_QUERY, theme);
    await settle(page);
    await page.screenshot({ path: `${dir("AT-28")}/${width}-${theme}.png`, fullPage: true });
    const rows = await page.locator(`${HERO} [data-mesh-anchor]`).evaluateAll((els) => els.map((el) => el.textContent?.replace(/\s+/g, " ").trim()));
    const heads = await page.locator(`${HERO} [data-mesh-hole][title]`).count();
    const imgs = await page.locator(`${HERO} img`).evaluateAll((els) => els.map((el) => el.getAttribute("src")));
    log("AT-28", `${width} ${theme}: stage rows: ${rows.join(" | ")}; headshot tokens: ${heads}; img elements in the hero: ${imgs.length ? imgs.join(", ") : "none"}`);
    await ctx.close();
  }
});

test("AT-4 and AT-9 keyboard tap, attributes, and the accessibility tree", async ({ browser }) => {
  reset("AT-4", CMD); reset("AT-9", CMD);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { ctx, page } = await newPage(browser, width);
    await openAnalyzer(page, T_QUERY, theme);
    await holdAnalyze(page);
    await settle(page);
    const button = page.getByRole("button", { name: "Grade the Trade" });
    await button.focus();
    await startWait(page, 3, "none");
    await page.keyboard.press("Enter");
    await untilElapsed(page, 2000);
    const attrs = await page.evaluate(() => {
      const b = document.activeElement as HTMLElement;
      const all = [...document.querySelectorAll("button")].filter((x) => x.textContent?.trim() === "Grade the Trade");
      const btn = all[0];
      return { activeIsButton: b === btn, active: `${b.tagName.toLowerCase()} "${b.textContent?.trim()}"`, ariaBusy: btn?.getAttribute("aria-busy"), dataPending: btn?.getAttribute("data-pending"), ariaDisabled: btn?.getAttribute("aria-disabled"), disabled: btn?.disabled, label: btn?.textContent?.trim(), slot: btn?.getAttribute("data-slot"), outer: btn?.outerHTML.slice(0, 400) };
    });
    log("AT-4", `${width} ${theme}: 2 s into the wait (Enter key on the focused button): ${JSON.stringify(attrs)}`);
    await button.screenshot({ path: `${dir("AT-4")}/${width}-${theme}.png` });
    const snap2 = await page.locator("body").ariaSnapshot();
    await page.locator(WAIT_HERO).screenshot({ path: `${dir("AT-9")}/2s-${width}-${theme}.png` });
    await untilElapsed(page, 7000);
    const snap7 = await page.locator("body").ariaSnapshot();
    await page.locator(WAIT_HERO).screenshot({ path: `${dir("AT-9")}/7s-${width}-${theme}.png` });
    writeFileSync(`${dir("AT-9")}/aria-2s-${width}-${theme}.yaml`, snap2);
    writeFileSync(`${dir("AT-9")}/aria-7s-${width}-${theme}.yaml`, snap7);
    const s = await waitState(page);
    const shown = s.lines.map((l: { text: string }) => l.text);
    const status = (y: string) => y.split("\n").filter((l) => /status|Grading/i.test(l)).map((l) => l.trim()).join(" / ");
    const hasLine = (y: string) => shown.filter((t: string) => y.includes(t));
    log("AT-9", `${width} ${theme}: status lines at 2 s: ${status(snap2)} || at 7 s: ${status(snap7)} || stage lines shown on screen by 7 s: ${shown.join("; ")} || of those, in the tree at 2 s: ${JSON.stringify(hasLine(snap2))}, at 7 s: ${JSON.stringify(hasLine(snap7))}`);
    await ctx.close();
  }
});

test("S16 AT-15 shots and AT-16 out of view", async ({ browser }) => {
  reset("AT-15", CMD); reset("AT-16", CMD);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { ctx, page } = await newPage(browser, width);
    await openAnalyzer(page, T_QUERY, theme);
    await holdAnalyze(page);
    await settle(page);
    await startWait(page, 3);
    await untilElapsed(page, 5000);
    await page.locator(WAIT_HERO).screenshot({ path: `${dir("AT-15")}/${width}-${theme}.png` });
    // The page of the wait is too short for the hero to leave the view, so the harness adds an empty 2000 px block at
    // the end of the body. The block is part of the instrument, not of the product.
    const natural = await page.evaluate((h) => ({ page: document.documentElement.scrollHeight, heroBottom: Math.round((document.querySelector(h) as HTMLElement).getBoundingClientRect().bottom + scrollY) }), WAIT_HERO);
    log("AT-16", `${width} ${theme}: the page of the wait is ${natural.page} px tall and the hero ends at ${natural.heroBottom} px, so a 900 px view cannot scroll the hero out; the harness adds an empty 2000 px block at the end of the body`);
    await page.evaluate(() => { const d = document.createElement("div"); d.setAttribute("data-evidence-spacer", ""); d.style.height = "2000px"; document.body.appendChild(d); });
    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
    await expect(page.locator(WAIT_HERO)).not.toBeInViewport();
    await page.waitForTimeout(300);
    const c = `${WAIT_HERO} canvas[data-hero-mesh]`;
    const a = await frames(page, c);
    await page.waitForTimeout(2000);
    const b = await frames(page, c);
    await page.screenshot({ path: `${dir("AT-16")}/${width}-${theme}.png` });
    log("AT-16", `${width} ${theme}: hero out of view: data-mesh-frames ${a} -> ${b} over 2 s (${b - a} frames)`);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(1000);
    const back = await frames(page, c);
    log("AT-16", `${width} ${theme}: back in view 1 s later: data-mesh-frames ${back} (${back - b} frames)`);
    // A hidden tab: a second tab comes to the front, then the page reports hidden.
    const other = await ctx.newPage();
    await other.bringToFront();
    await page.waitForTimeout(300);
    let state = await page.evaluate(() => document.visibilityState);
    let how = "a second tab brought to the front";
    if (state !== "hidden") {
      how = "the page reports hidden through a visibilitychange event, because headless Chromium keeps a background tab visible";
      await page.evaluate(() => {
        Object.defineProperty(document, "hidden", { configurable: true, get: () => true });
        Object.defineProperty(document, "visibilityState", { configurable: true, get: () => "hidden" });
        document.dispatchEvent(new Event("visibilitychange"));
      });
      state = await page.evaluate(() => document.visibilityState);
    }
    await page.waitForTimeout(300);
    const h0 = await frames(page, c);
    await page.waitForTimeout(2000);
    const h1 = await frames(page, c);
    log("AT-16", `${width} ${theme}: tab hidden (${how}; visibilityState ${state}): data-mesh-frames ${h0} -> ${h1} over 2 s (${h1 - h0} frames)`);
    await ctx.close();
  }
});

test("AT-15 frames at 375 with 4x CPU slowdown, 4 separate runs", async ({ browser }) => {
  for (let run = 1; run <= 4; run++) {
    // Each run is a fresh browser context, so no run shares a page, a cache of the canvas, or a timer with another.
    const { ctx, page } = await newPage(browser, 375, { viewport: { width: 375, height: 812 } });
    await openAnalyzer(page, T_QUERY, "dark");
    await holdAnalyze(page);
    await settle(page);
    const cdp = await ctx.newCDPSession(page);
    await cdp.send("Emulation.setCPUThrottlingRate", { rate: 4 });
    await page.evaluate(() => { const w = window as any; w.frameTimes = []; const tick = (n: number) => { w.frameTimes.push(n); requestAnimationFrame(tick); }; requestAnimationFrame(tick); });
    await browser.startTracing(page, { path: `${dir("AT-15")}/trace-375-4x-run${run}.json`, screenshots: false });
    await startWait(page, 3);
    const tapped = await page.evaluate(() => (window as any).wait.t0 as number);
    await page.waitForTimeout(5200);
    await browser.stopTracing();
    const times: number[] = await page.evaluate(([from, to]) => (window as any).frameTimes.filter((t: number) => t >= from && t <= to), [tapped + 1000, tapped + 5000]);
    const deltas = times.slice(1).map((t, i) => t - times[i]);
    const longest = Math.max(...deltas);
    writeFileSync(`${dir("AT-15")}/frames-375-4x-run${run}.txt`, `# Run ${run} of 4: rAF frame gaps in ms from 1 s to 5 s after the tap, 375 px, CPU slowdown 4x\n${deltas.map((d) => d.toFixed(1)).join("\n")}\n`);
    log("AT-15", `run ${run} of 4, 375 dark, 4x CPU slowdown: ${deltas.length} frames from 1 s to 5 s after the tap; longest frame after the first second ${longest.toFixed(1)} ms; mean ${(deltas.reduce((a, b) => a + b, 0) / deltas.length).toFixed(1)} ms; frames over 50 ms: ${deltas.filter((d) => d > 50).length}`);
    await cdp.send("Emulation.setCPUThrottlingRate", { rate: 1 });
    await ctx.close();
  }
});

/* Trade B through the Stack, as the e2e spec opens it. */
async function openTradeB(page: Page, theme: "light" | "dark") {
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
export { openTradeB };

test("AT-27 trade B", async ({ browser }) => {
  reset("AT-27", CMD);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { ctx, page } = await newPage(browser, width);
    await openTradeB(page, theme);
    await holdAnalyze(page);
    await settle(page);
    await startWait(page, 0);
    await untilElapsed(page, 1500);
    await page.locator(WAIT_HERO).screenshot({ path: `${dir("AT-27")}/${width}-${theme}.png` });
    const rows = await page.locator(`${WAIT_HERO} [data-mesh-anchor]`).evaluateAll((els) => els.map((el) => `${el.querySelector("[data-stage-team]")?.textContent}: ${[...el.querySelectorAll("[data-mesh-hole][title]")].map((t) => `${t.getAttribute("title")}${(t.querySelector("img") as HTMLImageElement | null)?.naturalWidth ? " [photo]" : " [initials]"}`).join(", ")}${el.textContent?.match(/\+\d+/) ? ` + token "${el.textContent.match(/\+\d+/)![0]}"` : ""} (height ${el.getBoundingClientRect().height.toFixed(0)} px)`));
    log("AT-27", `${width} ${theme}: ${rows.length} rows: ${rows.join(" | ")}`);
    await ctx.close();
  }
});

test("AT-33 trade L, long line, motion on", async ({ browser }) => {
  reset("AT-33", CMD);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const rec = width === 375 && theme === "dark";
    const { ctx, page } = await newPage(browser, width, rec ? { recordVideo: { dir: `${SCR}/r2-video-at33`, size: { width: 375, height: 900 } } } : {});
    await openAnalyzer(page, L_QUERY, theme);
    await holdAnalyze(page);
    await settle(page);
    await startWait(page, 2);
    // Each line: its text, the font size, its width, the width of its box and of the hero, and its scroll.
    const seen: string[] = [];
    let longStart = false;
    for (;;) {
      const now = await page.evaluate((hero) => {
        const live = document.querySelector(`${hero} .t-think-text:not(.is-exit)`) as HTMLElement;
        const box = document.querySelector(`${hero} .t-think`) as HTMLElement;
        const heroEl = document.querySelector(hero) as HTMLElement;
        const w = (window as any).wait;
        return { t: performance.now() - w.t0, text: live.textContent, font: getComputedStyle(live).fontSize, boxFont: getComputedStyle(box).fontSize, width: live.scrollWidth, box: box.clientWidth, hero: heroEl.clientWidth, cls: live.className, scroll: live.style.getPropertyValue("--think-scroll"), translate: getComputedStyle(live).translate, transform: getComputedStyle(live).transform, right: live.getBoundingClientRect().right, boxRight: box.getBoundingClientRect().right, left: live.getBoundingClientRect().left };
      }, WAIT_HERO);
      if (!seen.includes(now.text!)) {
        seen.push(now.text!);
        log("AT-33", `${width} ${theme}: ${now.t.toFixed(0)} ms "${now.text}": font ${now.font} (box ${now.boxFont}), line width ${now.width} px, line box ${now.box} px, hero ${now.hero} px, class "${now.cls}", --think-scroll ${now.scroll || "none"}`);
        if (now.text!.startsWith("Checking Unsolicited")) {
          await page.waitForTimeout(250);
          await page.locator(WAIT_HERO).screenshot({ path: `${dir("AT-33")}/start-${width}-${theme}.png` });
          longStart = true;
          const s = await page.evaluate((hero) => { const l = document.querySelector(`${hero} .t-think-text:not(.is-exit)`) as HTMLElement; const b = document.querySelector(`${hero} .t-think`) as HTMLElement; return `start shot: line left ${l.getBoundingClientRect().left.toFixed(1)}, right ${l.getBoundingClientRect().right.toFixed(1)}, box ${b.getBoundingClientRect().left.toFixed(1)}-${b.getBoundingClientRect().right.toFixed(1)}`; }, WAIT_HERO);
          log("AT-33", `${width} ${theme}: ${s}`);
          // Sample the move of the line every 100 ms until its rest at the end.
          const path: string[] = [];
          for (let k = 0; k < 20; k++) {
            const x = await page.evaluate((hero) => { const l = document.querySelector(`${hero} .t-think-text:not(.is-exit)`) as HTMLElement; return `${l.getBoundingClientRect().left.toFixed(1)}/${l.getBoundingClientRect().right.toFixed(1)}`; }, WAIT_HERO);
            path.push(x);
            await page.waitForTimeout(100);
            if (k === 17) await page.locator(WAIT_HERO).screenshot({ path: `${dir("AT-33")}/end-${width}-${theme}.png` });
          }
          log("AT-33", `${width} ${theme}: the left/right edge of the long line every 100 ms from the start shot: ${path.join(" ")}`);
        }
      }
      if (now.t > 30500) break;
      await page.waitForTimeout(80);
    }
    if (!longStart) log("AT-33", `${width} ${theme}: the long line did not show in 30 s`);
    await ctx.close();
    if (rec) log("AT-33", `375 dark: video ${await page.video()?.path()}`);
  }
});
