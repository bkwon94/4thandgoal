/* The wait with reduced motion: AT-13 (wait part), AT-14, and AT-34. */
import { test } from "@playwright/test";
import { openAnalyzer, serveDir, SCR, T_QUERY, WAIT_HERO, dir, log, reset, holdAnalyze, newPage, startWait, waitState, untilElapsed, WIDTHS, THEMES } from "./lib";
const CMD = "EV_TESTS=<scratch>/pw2/tests pnpm exec playwright test --config pw-evidence.config.ts reduced  (see steps.txt)";
const L_QUERY = "?team=2&with=11&give=8144&get=9502";
let srv: { close: () => Promise<void> };
test.beforeAll(async () => { srv = await serveDir(`${SCR}/r2-out-cpc`, 4173); });
test.afterAll(async () => { await srv.close(); });
const R = { reducedMotion: "reduce" };

test("AT-13 wait part and AT-14 lines, reduced motion", async ({ browser }) => {
  reset("AT-14", CMD);
  reset("AT-13", CMD);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { ctx, page } = await newPage(browser, width, R);
    await openAnalyzer(page, T_QUERY, theme);
    await holdAnalyze(page);
    await startWait(page, 3);
    await untilElapsed(page, 1000);
    const a = await page.locator(WAIT_HERO).screenshot({ path: `${dir("AT-13")}/wait-a-${width}-${theme}.png` });
    const pix = () => page.locator(`${WAIT_HERO} canvas[data-hero-mesh]`).evaluate((el) => { const c = el as HTMLCanvasElement; const d = c.getContext("2d")!.getImageData(0, 0, c.width, c.height).data; (window as any).px = (window as any).px ?? []; (window as any).px.push(d); const all = (window as any).px; let diff = 0; if (all.length === 2) for (let k = 0; k < d.length; k += 4) if (all[0][k] !== d[k] || all[0][k + 1] !== d[k + 1] || all[0][k + 2] !== d[k + 2] || all[0][k + 3] !== d[k + 3]) diff++; return `frames ${c.dataset.meshFrames}, ${diff} px differ from the first sample, of ${d.length / 4}`; });
    const ca = await pix();
    await page.locator(WAIT_HERO).screenshot({ path: `${dir("AT-14")}/line-1-${width}-${theme}.png` });
    await untilElapsed(page, 3000);
    const b = await page.locator(WAIT_HERO).screenshot({ path: `${dir("AT-13")}/wait-b-${width}-${theme}.png` });
    const cb = await pix();
    await page.locator(WAIT_HERO).screenshot({ path: `${dir("AT-14")}/line-2-${width}-${theme}.png` });
    const fr = await page.locator(`${WAIT_HERO} canvas[data-hero-mesh]`).evaluate((el) => `${(el as HTMLCanvasElement).dataset.meshFrames} frames, pulls ${(el as HTMLCanvasElement).dataset.meshPulls}`);
    log("AT-13", `${width} ${theme}: canvas pixels (getImageData) at 1 s: ${ca}; at 3 s: ${cb}; the full hero shots are byte-equal: ${a.equals(b)} (the stage line differs); canvas ${fr}`);
    await untilElapsed(page, 6200);
    const s = await waitState(page);
    const anim = await page.evaluate((hero) => {
      const els = [...document.querySelectorAll(`${hero} .t-think, ${hero} .t-think *`)];
      return els.map((el) => { const cs = getComputedStyle(el); const b = getComputedStyle(el, "::before"); const af = getComputedStyle(el, "::after"); return `${el.className}: animation ${cs.animationName}, ::before ${b.animationName} (duration ${b.animationDuration}, play ${b.animationPlayState}, display ${b.display}, visibility ${b.visibility}, opacity ${b.opacity}, content ${b.content.slice(0, 20)}), ::after ${af.animationName}`; }).join(" ; ") + ` || running animations in the hero: ${document.getAnimations().filter((x) => { const t = (x.effect as KeyframeEffect)?.target as Element | null; return t && document.querySelector(hero)?.contains(t); }).map((x) => (x as CSSAnimation).animationName ?? x.constructor.name).join(", ") || "none"}`;
    }, WAIT_HERO);
    log("AT-14", `${width} ${theme}: lines in 6.2 s: ${s.lines.map((l: { t: number; text: string }) => `${l.t.toFixed(0)} ms "${l.text}"`).join(", ")}`);
    log("AT-14", `${width} ${theme}: styles of the line: ${anim}`);
    await ctx.close();
  }
});

test("AT-34 trade L, reduced motion", async ({ browser }) => {
  reset("AT-34", CMD);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { ctx, page } = await newPage(browser, width, R);
    await openAnalyzer(page, L_QUERY, theme);
    await holdAnalyze(page);
    await startWait(page, 2);
    let found = false;
    for (;;) {
      const s = await waitState(page);
      const cur = s.lines.at(-1)?.text ?? "";
      if (cur.startsWith("Checking Unsolicited")) {
        await page.waitForTimeout(300);
        const m = async () => page.evaluate((hero) => { const l = document.querySelector(`${hero} .t-think-text:not(.is-exit)`) as HTMLElement; const b = document.querySelector(`${hero} .t-think`) as HTMLElement; const r = l.getBoundingClientRect(); return `"${l.textContent}" class "${l.className}", font ${getComputedStyle(l).fontSize}, line height ${getComputedStyle(l).lineHeight}, box ${b.clientWidth} px, text rect ${r.left.toFixed(1)},${r.top.toFixed(1)} ${r.width.toFixed(1)}x${r.height.toFixed(1)}, lines ${Math.round(r.height / parseFloat(getComputedStyle(l).lineHeight))}, white-space ${getComputedStyle(l).whiteSpace}, transform ${getComputedStyle(l).transform}`; }, WAIT_HERO);
        const m1 = await m();
        await page.locator(WAIT_HERO).screenshot({ path: `${dir("AT-34")}/a-${width}-${theme}.png` });
        await page.waitForTimeout(1000);
        const m2 = await m();
        await page.locator(WAIT_HERO).screenshot({ path: `${dir("AT-34")}/b-${width}-${theme}.png` });
        log("AT-34", `${width} ${theme}: shot a: ${m1}`);
        log("AT-34", `${width} ${theme}: shot b, 1 s later: ${m2}`);
        found = true;
        break;
      }
      if (s.now > 31000) break;
      await page.waitForTimeout(100);
    }
    if (!found) log("AT-34", `${width} ${theme}: the long line did not show in 31 s`);
    await ctx.close();
  }
});
