/* AT-20: the pixel scan of the analyzer hero in idle and in the wait, for cpc (trade T) and norcal (the recorded trade). */
import { test, type Page } from "@playwright/test";
import { openAnalyzer, serveDir, SCR, HERO, WAIT_HERO, T_QUERY, dir, log, holdAnalyze, settle, newPage, startWait, waitState } from "./lib";
import { rateEachHeroText } from "../../ev2/apps/site/e2e/floorx";
const N_QUERY = "?team=4&with=6&give=8132&get=8144,6130";
const lineAtRest = (page: Page) => page.evaluate(() => Promise.all(document.getAnimations().filter((a) => a.effect?.getComputedTiming().endTime !== Infinity).map((a) => a.finished.catch(() => undefined))));
type Row = { hero: string; text: string; ratio: number | null };
const worst = (rows: Row[]) => {
  const m = new Map<string, number>();
  for (const r of rows) if (r.ratio !== null) m.set(r.text, Math.min(m.get(r.text) ?? Infinity, r.ratio));
  return [...m.entries()].map(([t, v]) => `${t} ${v.toFixed(2)}:1`).join("\n    ");
};
for (const [client, query] of [["cpc", T_QUERY], ["norcal", N_QUERY]] as const) {
  test(`AT-20 ${client} idle and wait`, async ({ browser }) => {
    const srv = await serveDir(`${SCR}/r2-out-${client}`, 4173);
    for (const width of [375, 390, 768, 1280]) for (const theme of ["light", "dark"] as const) {
      const scan = width === 390 || width === 1280;
      const { ctx, page } = await newPage(browser, width);
      await openAnalyzer(page, query, theme);
      await holdAnalyze(page);
      await settle(page);
      if (scan) log("AT-20", `${client} idle ${width} ${theme}: worst ratio of each hero text:\n    ${worst(await rateEachHeroText(page, HERO))}`);
      if (width !== 390) await page.locator(HERO).screenshot({ path: `${dir("AT-20")}/${client}-idle-${width}-${theme}.png` });
      await startWait(page, 0);
      await page.waitForTimeout(300);
      if (scan) {
        const rows: Row[] = [];
        let n = 0;
        const t0 = (await waitState(page)).now;
        while (n < 10 || (await waitState(page)).now - t0 < 3000) {
          await lineAtRest(page);
          rows.push(...(await rateEachHeroText(page, WAIT_HERO)));
          n++;
          await page.waitForTimeout(150);
        }
        log("AT-20", `${client} wait ${width} ${theme}: ${n} samples over ${((await waitState(page)).now - t0).toFixed(0)} ms; worst ratio of each hero text over all samples:\n    ${worst(rows)}`);
      }
      if (width !== 390) await page.locator(WAIT_HERO).screenshot({ path: `${dir("AT-20")}/${client}-wait-${width}-${theme}.png` });
      await ctx.close();
    }
    await srv.close();
  });
}
