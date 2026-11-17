/* AT-32: a real trade of 3 sides at 375 px whose fairness reason runs past 3 lines. */
import { test, expect, type Page } from "@playwright/test";
import { writeFileSync } from "node:fs";
import { openTradeB, serveDir, SCR, dir, log, reset, newPage } from "./lib";

const CMD = "EV_TESTS=<scratch>/pw/tests pnpm exec playwright test --config pw-evidence.config.ts fold  (see steps.txt)";
/* Each fairness reason of the read: its text, its lines, and whether it shows More. */
const reasons = (page: Page) => page.evaluate(() => [...document.querySelectorAll("main p.line-clamp-3, main p[class*='line-clamp-3'], main p.max-w-measure.text-lead")].filter((p) => p.closest("div.flex.flex-col.items-start")).map((p) => {
  const el = p as HTMLElement;
  const lh = parseFloat(getComputedStyle(el).lineHeight);
  const more = el.parentElement?.querySelector("button");
  return { text: el.textContent ?? "", shown: Math.round(el.getBoundingClientRect().height / lh), full: Math.round(el.scrollHeight / lh), more: !!more && more.textContent?.trim() === "More" };
}));
test("AT-32 trade B", async ({ browser }) => {
  reset("AT-32", CMD);
  const srv = await serveDir(`${SCR}/out-cpc`, 4173);
  const { ctx, page } = await newPage(browser, 375);
  await openTradeB(page, "dark");
  const resp = page.waitForResponse((r) => r.url().endsWith("/analyze") && r.request().method() === "POST", { timeout: 240000 });
  const t0 = Date.now();
  await page.getByRole("button", { name: "Grade the Trade" }).click();
  const r = await resp;
  writeFileSync(`${SCR}/answer-B.json`, await r.text());
  await expect(page.getByRole("tablist", { name: "The sides" })).toBeVisible({ timeout: 30000 });
  await page.waitForTimeout(2000);
  log("AT-32", `trade B, real grade at 375 dark: HTTP ${r.status()} after ${Date.now() - t0} ms`);
  for (const x of await reasons(page)) log("AT-32", `375 dark: reason "${x.text}" shows ${x.shown} lines of ${x.full}; More ${x.more}`);
  await ctx.close(); await srv.close();
});

test("AT-32 shots before and after More", async ({ browser }) => {
  const srv = await serveDir(`${SCR}/out-cpc`, 4173);
  for (const width of [375, 768, 1280]) for (const theme of ["light", "dark"] as const) {
    const { ctx, page } = await newPage(browser, width);
    await openTradeB(page, theme);
    await page.getByRole("button", { name: "Grade the Trade" }).click();
    await expect(page.getByRole("tablist", { name: "The sides" })).toBeVisible({ timeout: 120000 });
    await page.waitForTimeout(2000);
    const reason = page.locator("p").filter({ hasText: "The Blue Tent adds McCaffrey and Henry" }).last();
    await reason.scrollIntoViewIfNeeded();
    const card = reason.locator("xpath=ancestor::div[contains(@class,'rounded')][1]");
    const measure = () => reason.evaluate((el) => { const lh = parseFloat(getComputedStyle(el).lineHeight); return `${Math.round(el.getBoundingClientRect().height / lh)} lines shown of ${Math.round(el.scrollHeight / lh)}, clipped ${el.scrollHeight > el.clientHeight + 1}`; });
    const more = reason.locator("xpath=..").getByRole("button", { name: "More", exact: true });
    const before = await measure();
    const hasMore = await more.count();
    await card.screenshot({ path: `${dir("AT-32")}/before-${width}-${theme}.png` });
    let after = "no More to tap";
    if (hasMore) {
      const box = (await more.boundingBox())!;
      await more.click();
      await page.waitForTimeout(300);
      after = `${await measure()}; More target was ${box.width.toFixed(0)} x ${box.height.toFixed(0)} px; More buttons left ${await more.count()}`;
    }
    await card.screenshot({ path: `${dir("AT-32")}/after-${width}-${theme}.png` });
    log("AT-32", `${width} ${theme}: The Blue Tent reason before: ${before}, More shown ${hasMore > 0}; after the tap: ${after}`);
    await ctx.close();
  }
  await srv.close();
});
