/* Pages and parts outside the grade: AT-17 (static heroes), AT-19, AT-21, AT-23, AT-24. */
import { test, expect, type Page } from "@playwright/test";
import { openAnalyzer, openPage, serveDir, SCR, BASE, dir, log, reset, newPage, WIDTHS, THEMES, plateScan, fmtPlate } from "./lib";
import { rateEachHeroText } from "../../ev2/apps/site/e2e/floorx";
const CMD = "EV_TESTS=<scratch>/pw2/tests pnpm exec playwright test --config pw-evidence.config.ts pages  (see steps.txt)";
const fmt = (rows: { hero: string; text: string; ratio: number | null }[]) => rows.map((r) => `${r.hero} | ${r.text} | ${r.ratio === null ? "no pixel" : r.ratio.toFixed(2)}:1`).join("\n    ");

test.describe("cpc", () => {
  let srv: { close: () => Promise<void> };
  test.beforeAll(async () => { srv = await serveDir(`${SCR}/r2-out-cpc`, 4173); });
  test.afterAll(async () => { await srv.close(); });

  test("AT-17 static heroes", async ({ browser }) => {
    reset("AT-17", CMD);
    const pages = [["week-09", "/2026/week-09/"], ["manager-bo-girds", "/2026/managers/6/"], ["midseason", "/midseason/2026/"], ["404", "/no-such-page/"]];
    for (const [name, route] of pages) for (const width of WIDTHS) for (const theme of THEMES) {
      const { ctx, page } = await newPage(browser, width);
      await openPage(page, `${BASE}${route}`, theme);
      await page.waitForTimeout(800);
      const hero = page.locator("main section").first();
      await hero.screenshot({ path: `${dir("AT-17")}/${name}-${width}-${theme}.png` });
      log("AT-17", `${name} ${width} ${theme}: ${fmtPlate(await plateScan(page, "main section"))}`);
      await ctx.close();
    }
  });

  test("AT-19 the losing score", async ({ browser }) => {
    reset("AT-19", CMD);
    for (const width of [390, 1280]) for (const theme of THEMES) {
      const { ctx, page } = await newPage(browser, width);
      await openPage(page, `${BASE}/2026/week-09/`, theme);
      await page.waitForTimeout(800);
      const rows = await rateEachHeroText(page);
      const score = rows.filter((r) => r.text.includes("106.71"));
      log("AT-19", `${width} ${theme}: pixel scan of the week 9 hero, the texts with 106.71: ${score.length ? score.map((r) => `${r.text} ${r.ratio?.toFixed(2)}:1`).join("; ") : "none found"}`);
      log("AT-19", `${width} ${theme}: every hero text:\n    ${fmt(rows)}`);
      await ctx.close();
    }
    for (const width of WIDTHS) for (const theme of THEMES) {
      const { ctx, page } = await newPage(browser, width);
      await openPage(page, `${BASE}/2026/week-09/`, theme);
      await page.waitForTimeout(800);
      await page.locator("main section").first().screenshot({ path: `${dir("AT-19")}/${width}-${theme}.png` });
      await ctx.close();
    }
  });

  test("AT-21 egg banner", async ({ browser }) => {
    reset("AT-21", CMD);
    const drop = await fetch("http://localhost:8080/clients/cpc/eggs/drop", { method: "POST", headers: { "Content-Type": "application/json", "X-Commissioner-Key": "localkey" }, body: JSON.stringify({ week: 9, eggs: [{ page: "/midseason/2026/", target: "luck-3", action: "tap2", conditions: { theme: "light" } }] }) });
    log("AT-21", `the drop of test egg T1 of eggs.spec.ts to the local API (week 9): HTTP ${drop.status}`);
    for (const width of [390, 1280]) for (const theme of THEMES) {
      const { ctx, page } = await newPage(browser, width);
      await page.addInitScript(() => localStorage.setItem("cpc.passphrase", "localtest"));
      await openPage(page, `${BASE}/`, theme);
      await expect(page.locator("section.hero-texture")).toBeVisible({ timeout: 20000 });
      await page.waitForTimeout(800);
      const rows = await rateEachHeroText(page, "section.hero-texture");
      log("AT-21", `${width} ${theme}: pixel scan of the egg banner:\n    ${fmt(rows)}`);
      await ctx.close();
    }
    for (const width of WIDTHS) for (const theme of THEMES) {
      const { ctx, page } = await newPage(browser, width);
      await page.addInitScript(() => localStorage.setItem("cpc.passphrase", "localtest"));
      await openPage(page, `${BASE}/`, theme);
      await expect(page.locator("section.hero-texture")).toBeVisible({ timeout: 20000 });
      await page.waitForTimeout(800);
      await page.locator("section.hero-texture").screenshot({ path: `${dir("AT-21")}/${width}-${theme}.png` });
      await ctx.close();
    }
  });

  test("AT-24 front door chat wait", async ({ browser }) => {
    reset("AT-24", CMD);
    for (const width of WIDTHS) for (const theme of THEMES) {
      const { ctx, page } = await newPage(browser, width);
      await page.addInitScript(() => localStorage.setItem("cpc.passphrase", "localtest"));
      // The answer is held, so the wait stays on the screen. The real request goes to the local API on no release.
      await page.route(/\/ask(\/free)?$/, () => undefined);
      await openPage(page, `${BASE}/`, theme);
      const pick = page.getByRole("dialog").getByRole("button", { name: /Bo Girds/ });
      if (await pick.count()) await pick.first().click(); else await page.getByRole("dialog").getByRole("button").first().click().catch(() => undefined);
      const field = page.getByRole("textbox", { name: "Ask a question" });
      await field.fill("Who should I start this week?");
      await page.getByRole("button", { name: "Send" }).click();
      await page.waitForTimeout(1500);
      await page.screenshot({ path: `${dir("AT-24")}/${width}-${theme}.png` });
      const m = await page.evaluate(() => ({ canvas: document.querySelectorAll("canvas[data-hero-mesh]").length, think: document.querySelectorAll(".t-think").length, grading: document.querySelectorAll('section[aria-label="Grading the Trade"]').length, status: [...document.querySelectorAll('[role="status"], [aria-busy="true"]')].map((e) => `${e.tagName.toLowerCase()} "${(e.textContent ?? "").trim().slice(0, 50)}"`) }));
      log("AT-24", `${width} ${theme}: 1.5 s after Send with the answer in progress: mesh canvases ${m.canvas}, stage line parts (.t-think) ${m.think}, grading heroes ${m.grading}; status parts: ${m.status.join(", ") || "none"}`);
      await ctx.close();
    }
  });
});

test.describe("norcal", () => {
  let srv: { close: () => Promise<void> };
  test.beforeAll(async () => { srv = await serveDir(`${SCR}/r2-out-norcal`, 4173); });
  test.afterAll(async () => { await srv.close(); });
  test("AT-23 Finder wait", async ({ browser }) => {
    reset("AT-23", CMD);
    for (const width of WIDTHS) for (const theme of THEMES) {
      const { ctx, page } = await newPage(browser, width);
      await page.route(/\/find$/, async (route) => { if (route.request().method() !== "POST") return route.continue(); });
      await page.addInitScript(() => localStorage.setItem("cpc.passphrase", "localtest"));
      await openAnalyzer(page, "?team=4", theme);
      await page.getByRole("button", { name: "Find a Trade" }).click();
      const finder = page.locator('section[aria-labelledby="find-trade"]');
      await expect(finder.getByRole("button", { name: "Finding…" })).toBeVisible();
      await page.waitForTimeout(1200);
      await finder.scrollIntoViewIfNeeded();
      await page.screenshot({ path: `${dir("AT-23")}/${width}-${theme}.png` });
      const m = await page.evaluate(() => ({ sweep: document.querySelectorAll('section[aria-labelledby="find-trade"] [role="presentation"]').length, sweepClass: [...document.querySelectorAll('section[aria-labelledby="find-trade"] [role="presentation"] *, section[aria-labelledby="find-trade"] [role="presentation"]')].map((e) => e.className).filter(Boolean).slice(0, 3), finderCanvas: document.querySelectorAll('section[aria-labelledby="find-trade"] canvas').length, grading: document.querySelectorAll('section[aria-label="Grading the Trade"]').length, think: document.querySelectorAll(".t-think").length }));
      log("AT-23", `${width} ${theme}: in the Finder wait: Sweep bar parts ${m.sweep} (classes ${JSON.stringify(m.sweepClass)}), canvases in the Finder ${m.finderCanvas}, grading heroes ${m.grading}, stage line parts ${m.think}`);
      await ctx.close();
    }
  });
});
