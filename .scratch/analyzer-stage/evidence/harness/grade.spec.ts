/* The tests that need a real grade: AT-10, 11, 12, 13 (reveal), 17 (result), 20 (reveal), 26, 30, 31, 32. */
import { test, expect, type Page } from "@playwright/test";
import { writeFileSync } from "node:fs";
import { openAnalyzer, serveDir, SCR, T_QUERY, READ_HERO, WAIT_HERO, dir, log, reset, holdAnalyze, settle, newPage, netLog, watchReveal, revealOf, watchRowLight, rowLightOf, plateScan, fmtPlate, WIDTHS, THEMES, type Reveal } from "./lib";
import { rateEachHeroText } from "../../ev2/apps/site/e2e/floorx";
const CMD = "EV_TESTS=<scratch>/pw2/tests pnpm exec playwright test --config pw-evidence.config.ts grade  (see steps.txt)";
const N_QUERY = "?team=4&with=6&give=8132&get=8144,6130";
const isAnalyze = (r: { url: () => string; request: () => { method: () => string } }) => r.url().endsWith("/analyze") && r.request().method() === "POST";
const stamps = (sent: number, r: Reveal) => (["lean", "scale", "case", "tabs"] as const).map((k) => `${k} ${r[k] === null ? "never" : `${r[k]! - sent} ms`}`).join(", ");

/* A first real grade, so later grades of the same trade are cached repeats. */
async function firstGrade(page: Page, query: string, theme: "light" | "dark", label: string) {
  const rows = netLog(page);
  await openAnalyzer(page, query, theme);
  const start = Date.now();
  const resp = page.waitForResponse(isAnalyze, { timeout: 240000 });
  await page.getByRole("button", { name: "Grade the Trade" }).click();
  const r = await resp;
  const took = Date.now() - start;
  const body = await r.text();
  writeFileSync(`${SCR}/answer-${label}.json`, body);
  await expect(page.locator(READ_HERO)).toBeVisible({ timeout: 30000 });
  return { took, doc: JSON.parse(body), rows, status: r.status() };
}

test("R0 the first real grade of trade T and of the norcal trade", async ({ browser }) => {
  reset("AT-26", CMD);
  reset("AT-12", CMD);
  let srv = await serveDir(`${SCR}/r2-out-cpc`, 4173);
  let { ctx, page } = await newPage(browser, 1280);
  const t = await firstGrade(page, T_QUERY, "dark", "T");
  await page.waitForTimeout(1500);
  writeFileSync(`${dir("AT-26")}/network-first-grade-1280-dark.txt`, `# The first grade of trade T on this day, not cached. The tap to the response took ${t.took} ms.\n${t.rows.join("\n")}\n`);
  const fav = t.doc.fairness?.state ?? "n/a";
  log("AT-12", `trade T, first real grade: HTTP ${t.status} after ${t.took} ms; Lean "${t.doc.lean}"; fairness ${fav}; the full answer is in answer-T.json`);
  writeFileSync(`${dir("AT-12")}/answer-T.json`, JSON.stringify(t.doc, null, 2));
  await ctx.close(); await srv.close();
  srv = await serveDir(`${SCR}/r2-out-norcal`, 4173);
  ({ ctx, page } = await newPage(browser, 1280));
  const n = await firstGrade(page, N_QUERY, "dark", "norcal");
  log("AT-12", `norcal trade of AT-20, first real grade: HTTP ${n.status} after ${n.took} ms; Lean "${n.doc.lean}"`);
  await ctx.close(); await srv.close();
});

test("AT-10, 11, 12, 17, 26, 30, 31 on a cached grade of trade T", async ({ browser }) => {
  for (const at of ["AT-10", "AT-11", "AT-30", "AT-31"]) reset(at, CMD);
  const srv = await serveDir(`${SCR}/r2-out-cpc`, 4173);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const rec = width === 1280 && theme === "dark";
    const { ctx, page } = await newPage(browser, width, rec ? { recordVideo: { dir: `${SCR}/r2-video-reveal`, size: { width: 1280, height: 900 } } } : {});
    const rows = netLog(page);
    await openAnalyzer(page, T_QUERY, theme);
    await settle(page);
    await watchReveal(page);
    await watchRowLight(page);
    let got = 0;
    const resp = page.waitForResponse(isAnalyze);
    await page.getByRole("button", { name: "Grade the Trade" }).click();
    const r = await resp;
    got = Date.now();
    await page.waitForTimeout(80);
    await page.locator(READ_HERO).screenshot({ path: `${dir("AT-12")}/flash-${width}-${theme}.png` }).catch(() => undefined);
    const flashAt = Date.now() - got;
    await page.waitForTimeout(Math.max(0, 650 - (Date.now() - got)));
    await page.locator(READ_HERO).screenshot({ path: `${dir("AT-12")}/dip-${width}-${theme}.png` }).catch(() => undefined);
    const dipAt = Date.now() - got;
    const reveal = await revealOf(page);
    log("AT-10", `${width} ${theme}: cached grade: the response came ${got} (clock ms); the Lean word at rest ${reveal.lean === null ? "never" : `${reveal.lean - got} ms`} after the response`);
    log("AT-11", `${width} ${theme}: each part at rest, from the response: ${stamps(got, reveal)}`);
    const peak = reveal.mesh.reduce((a, b) => (b.flash > a.flash ? b : a), reveal.mesh[0]);
    const pulls = reveal.mesh.map((m) => m.pulls);
    const maxPull = (i: number) => Math.max(...pulls.map((p) => p[i] ?? 0));
    const deepest = reveal.mesh.reduce((a, b) => (Math.max(...b.pulls, 0) > Math.max(...a.pulls, 0) ? b : a), reveal.mesh[0]);
    log("AT-12", `${width} ${theme}: flash peak ${peak?.flash} at ${peak ? peak.at - got : "?"} ms; deepest dip ${deepest ? Math.max(...deepest.pulls, 0).toFixed(3) : "?"} at ${deepest ? deepest.at - got : "?"} ms; max pull per side ${[0, 1].map((i) => maxPull(i).toFixed(3)).join(", ")}; last pulls ${reveal.mesh.at(-1)?.pulls.join(",")}; flash shot at ${flashAt} ms, dip shot at ${dipAt} ms`);
    const light = await rowLightOf(page);
    const f = (l: number[]) => l.map((v) => v.toFixed(0)).join(", ");
    const share = (l: number[]) => (l.length === 2 && l[0] + l[1] > 0 ? `; row 1 (Teehee) has ${((100 * l[1]) / Math.max(l[0], 1)).toFixed(1)}% of the light of row 0 (Bo Girds)` : "");
    log("AT-12", `${width} ${theme}: light of the read mesh in the box of each row (row 0 Bo Girds, row 1 Teehee): at the flash peak (flash ${light.flash.flash}) ${f(light.flash.sums)}${share(light.flash.sums)}; at the deepest dip (pull ${light.dip.pull}) ${f(light.dip.sums)}${share(light.dip.sums)}; at rest ${f(light.rest)}`);
    if (rec) writeFileSync(`${dir("AT-12")}/mesh-1280-dark.json`, JSON.stringify(reveal.mesh.map((m) => ({ t: m.at - got, flash: m.flash, pulls: m.pulls }))));
    await page.locator(READ_HERO).screenshot({ path: `${dir("AT-11")}/${width}-${theme}.png` });
    await page.locator(READ_HERO).screenshot({ path: `${dir("AT-17")}/analyzer-result-${width}-${theme}.png` });
    log("AT-17", `analyzer-result ${width} ${theme}: ${fmtPlate(await plateScan(page, READ_HERO))}`);
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1500);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(500);
    await page.screenshot({ path: `${dir("AT-10")}/${width}-${theme}.png`, fullPage: true });
    await page.screenshot({ path: `${dir("AT-30")}/${width}-${theme}.png`, fullPage: true });
    // AT-30: the parts below the hero.
    const heading = await page.getByRole("heading", { name: "The Trade", exact: true }).count();
    const group = await page.getByRole("group", { name: "The trade", exact: true }).count();
    for (const tab of await page.getByRole("tablist", { name: "The sides" }).getByRole("tab").all()) {
      await tab.click();
      const shown = await page.evaluate((hero) => {
        const read = document.querySelector(hero)!;
        const below = (el: Element) => !read.contains(el) && el.checkVisibility() && !!(read.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING);
        return { images: [...document.querySelectorAll("main img")].filter(below).map((i) => i.getAttribute("src")), chips: [...document.querySelectorAll("main li:has(> img)")].filter(below).length, fold: [...document.querySelectorAll("main [data-fold-line], main [class*='fold']")].filter(below).length };
      }, READ_HERO);
      log("AT-30", `${width} ${theme}: tab "${(await tab.textContent())?.trim()}": headings "The Trade" ${heading}, groups "The trade" ${group}, visible images below the hero ${shown.images.length}${shown.images.length ? ` (${shown.images.join(", ")})` : ""}, player chips ${shown.chips}, fold-line parts ${shown.fold}`);
    }
    // AT-31: Edit.
    const sides = page.getByRole("heading", { name: "The Sides", exact: true });
    const edit = page.getByRole("button", { name: "Edit the trade" });
    await edit.scrollIntoViewIfNeeded();
    const box = (await edit.boundingBox())!;
    const head = (await sides.boundingBox())!;
    log("AT-31", `${width} ${theme}: the Edit target is ${box.width.toFixed(1)} x ${box.height.toFixed(1)} px, at x ${box.x.toFixed(0)}, y ${box.y.toFixed(0)}; the heading The Sides ends at x ${(head.x + head.width).toFixed(0)}, y ${head.y.toFixed(0)}-${(head.y + head.height).toFixed(0)}`);
    await sides.locator("..").screenshot({ path: `${dir("AT-31")}/header-${width}-${theme}.png` });
    await edit.click();
    const stack = page.getByRole("region", { name: "Who gets what" });
    await expect(stack).toBeInViewport();
    await page.waitForTimeout(700);
    const text = (await stack.textContent())?.replace(/\s+/g, " ") ?? "";
    log("AT-31", `${width} ${theme}: after Edit the Stack "Who gets what" is in view; it names Tee Higgins ${text.includes("Tee Higgins")}, Bhayshul Tuten ${text.includes("Bhayshul Tuten")}, Kenneth Walker III ${text.includes("Kenneth Walker III")}`);
    await page.screenshot({ path: `${dir("AT-31")}/stack-${width}-${theme}.png` });
    const analyze = rows.filter((l) => l.includes("/analyze"));
    log("AT-26", `${width} ${theme}: analyze calls in the network log: ${analyze.join(" || ")}`);
    if (rec) writeFileSync(`${dir("AT-26")}/network-cached-grade-1280-dark.txt`, rows.join("\n") + "\n");
    await page.screenshot({ path: `${dir("AT-26")}/${width}-${theme}.png`, fullPage: true });
    await ctx.close();
    if (rec) log("AT-11", `1280 dark: video ${await page.video()?.path()} (it is also the recording of AT-12)`);
  }
  await srv.close();
});

test("AT-13 reveal with motion off", async ({ browser }) => {
  const srv = await serveDir(`${SCR}/r2-out-cpc`, 4173);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const rec = width === 1280 && theme === "dark";
    const { ctx, page } = await newPage(browser, width, { reducedMotion: "reduce", ...(rec ? { recordVideo: { dir: `${SCR}/r2-video-reduced`, size: { width: 1280, height: 900 } } } : {}) });
    await openAnalyzer(page, T_QUERY, theme);
    const held = await holdAnalyze(page);
    await page.getByRole("button", { name: "Grade the Trade" }).click();
    await expect(page.locator(WAIT_HERO)).toBeVisible();
    await page.waitForTimeout(1500);
    await watchReveal(page);
    const sent = Date.now();
    await held.release();
    const reveal = await revealOf(page);
    await page.locator(READ_HERO).screenshot({ path: `${dir("AT-13")}/result-${width}-${theme}.png` });
    log("AT-13", `${width} ${theme}: reveal with motion off: opacity of the result over the first 12 frames ${reveal.fade.slice(0, 12).map((o) => o.toFixed(2)).join(", ")}; last ${reveal.fade.at(-1)}; largest move of the Lean word ${reveal.leanMove.toFixed(2)} px; mesh flash max ${Math.max(0, ...reveal.mesh.map((m) => m.flash))}, pull max ${Math.max(0, ...reveal.mesh.flatMap((m) => m.pulls))}; ${stamps(sent, reveal)}`);
    await ctx.close();
    if (rec) log("AT-13", `1280 dark: video of the reveal ${await page.video()?.path()}`);
  }
  await srv.close();
});

test("AT-20 reveal end scans", async ({ browser }) => {
  for (const [client, query] of [["cpc", T_QUERY], ["norcal", N_QUERY]] as const) {
    const srv = await serveDir(`${SCR}/r2-out-${client}`, 4173);
    for (const width of [375, 390, 768, 1280]) for (const theme of THEMES) {
      const { ctx, page } = await newPage(browser, width);
      await openAnalyzer(page, query, theme);
      await settle(page);
      await watchReveal(page);
      await page.getByRole("button", { name: "Grade the Trade" }).click();
      await revealOf(page);
      await page.evaluate(() => Promise.all(document.getAnimations().filter((a) => a.effect?.getComputedTiming().endTime !== Infinity).map((a) => a.finished.catch(() => undefined))));
      if (width === 390 || width === 1280) {
        const rows = await rateEachHeroText(page, READ_HERO);
        log("AT-20", `${client} reveal end ${width} ${theme}: ratio of each hero text:\n    ${rows.map((r) => `${r.text} ${r.ratio === null ? "no pixel" : `${r.ratio.toFixed(2)}:1`}`).join("\n    ")}`);
      }
      if (width !== 390) await page.locator(READ_HERO).screenshot({ path: `${dir("AT-20")}/${client}-reveal-${width}-${theme}.png` });
      await ctx.close();
    }
    await srv.close();
  }
});
