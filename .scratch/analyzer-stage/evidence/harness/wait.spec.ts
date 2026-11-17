/* The wait of trade T with motion on: AT-3, AT-5, AT-6, AT-7, AT-29 in one session per width and theme. */
import { test } from "@playwright/test";
import { writeFileSync } from "node:fs";
import { openAnalyzer, serveDir, SCR, T_QUERY, WAIT_HERO, dir, log, reset, holdAnalyze, settle, newPage, startWait, waitState, untilElapsed, WIDTHS, THEMES } from "./lib";
const CMD = "EV_TESTS=<scratch>/pw2/tests pnpm exec playwright test --config pw-evidence.config.ts wait  (see steps.txt)";
test("wait of trade T", async ({ browser }) => {
  const srv = await serveDir(`${SCR}/r2-out-cpc`, 4173);
  for (const at of ["AT-3", "AT-5", "AT-6", "AT-7", "AT-29"]) reset(at, CMD);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const full = width === 1280 && theme === "dark";
    const { ctx, page } = await newPage(browser, width, full ? { recordVideo: { dir: `${SCR}/r2-video-wait`, size: { width: 1280, height: 900 } } } : {});
    await openAnalyzer(page, T_QUERY, theme);
    const held = await holdAnalyze(page);
    await settle(page);
    await startWait(page, 3);
    const hero = page.locator(WAIT_HERO);
    const shot = async (at: string, name: string) => {
      const t = (await waitState(page)).now;
      await hero.screenshot({ path: `${dir(at)}/${name}${width}-${theme}.png` });
      log(at, `${width} ${theme}: shot ${name}${width}-${theme}.png started ${t.toFixed(0)} ms after the tap`);
    };
    await shot("AT-3", "");
    await untilElapsed(page, 1000);
    await shot("AT-29", "");
    // AT-5: one shot at the deepest part of the first dip of each side.
    const dips: Record<number, boolean> = {};
    for (;;) {
      const s = await waitState(page);
      const p = s.pulls.at(-1)?.p ?? [];
      const top = Math.max(...p);
      const side = top > 0.45 ? p.indexOf(top) : -1;
      if (side >= 0 && !dips[side]) { dips[side] = true; await shot("AT-5", `dip-side-${side}-`); }
      if ((dips[0] && dips[1]) || s.now > 6000) break;
      await page.waitForTimeout(30);
    }
    await untilElapsed(page, 3200);
    await shot("AT-6", "line-2-");
    await untilElapsed(page, 5800);
    await shot("AT-6", "line-3-");
    await shot("AT-7", "");
    if (full) await untilElapsed(page, 30500);
    const s = await waitState(page);
    log("AT-3", `${width} ${theme}: "Weighing the sides" first in the DOM ${s.firstLine?.toFixed(1)} ms after the tap; two frames of the wait mesh differ at ${s.meshMoves?.toFixed(1)} ms`);
    log("AT-29", `${width} ${theme}: ${s.tokenCount} headshot tokens; the last token at rest ${s.tokensRest?.toFixed(0)} ms after the tap`);
    const rows = await page.locator(`${WAIT_HERO} [data-mesh-anchor]`).evaluateAll((els) => els.map((el) => `${el.querySelector("[data-stage-team]")?.textContent}: ${[...el.querySelectorAll("[data-mesh-hole][title]")].map((t) => `${t.getAttribute("title")} [${t.querySelector("img") ? `img ${t.querySelector("img")!.getAttribute("src")} loaded=${(t.querySelector("img") as HTMLImageElement).naturalWidth > 0}` : "initials"}]`).join(", ")}`));
    log("AT-29", `${width} ${theme}: rows: ${rows.join(" | ")}`);
    const lines = s.lines.map((l: { t: number; text: string }) => `${l.t.toFixed(0)} ms  ${l.text}`);
    log("AT-6", `${width} ${theme}: lines in the first ${(s.now / 1000).toFixed(1)} s:\n    ${lines.join("\n    ")}`);
    if (full) {
      log("AT-7", `${width} ${theme}: each line in ${(s.now / 1000).toFixed(1)} s of the wait:\n    ${lines.join("\n    ")}`);
      // The side that pulls hardest, by run, for the first 5 s.
      const runs: { side: number; from: number; to: number; peak: number }[] = [];
      for (const { t, p } of s.pulls as { t: number; p: number[] }[]) {
        if (t > 5200) break;
        const top = Math.max(...p, 0);
        const side = top > 0.05 ? p.indexOf(top) : -1;
        if (side < 0) continue;
        const run = runs.at(-1);
        if (run && run.side === side) { run.to = t; run.peak = Math.max(run.peak, top); } else runs.push({ side, from: t, to: t, peak: top });
      }
      log("AT-5", `1280 dark: side 0 is Bo Girds, side 1 is Teehee. Runs of the side that pulls hardest (pull > 0.05) in the first 5.2 s:\n    ${runs.map((r) => `side ${r.side}: ${r.from.toFixed(0)}-${r.to.toFixed(0)} ms, peak pull ${r.peak.toFixed(2)}`).join("\n    ")}`);
      writeFileSync(`${dir("AT-5")}/pulls-1280-dark.json`, JSON.stringify((s.pulls as { t: number; p: number[] }[]).filter((x) => x.t <= 5200).map((x) => ({ t: Math.round(x.t), p: x.p })), null, 0));
    }
    await ctx.close();
    if (full) log("AT-5", `1280 dark: video ${await page.video()?.path()}`);
    void held;
  }
  await srv.close();
});
