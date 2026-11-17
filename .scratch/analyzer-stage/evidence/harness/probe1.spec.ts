import { test } from "@playwright/test";
import { openAnalyzer, serveDir, SCR, HERO, log, newPage } from "./lib";
test("AT-1 pitch", async ({ browser }) => {
  const srv = await serveDir(`${SCR}/out-cpc`, 4173);
  const { ctx, page } = await newPage(browser, 1280);
  await openAnalyzer(page, "", "dark");
  await page.waitForTimeout(3000);
  const m = await page.evaluate((h) => { const c = document.querySelector(`${h} canvas[data-hero-mesh]`) as HTMLCanvasElement; return { grid: getComputedStyle(document.documentElement).getPropertyValue("--spacing-hero-grid"), pulls: c.dataset.meshPulls ?? "none", flash: c.dataset.meshFlash ?? "none", frames: c.dataset.meshFrames }; }, HERO);
  log("AT-1", `1280 dark: --spacing-hero-grid ${m.grid.trim()} (the pitch the mesh reads, see packages/design/site/parts/mesh-canvas.ts line 184); data-mesh-pulls ${m.pulls}; data-mesh-flash ${m.flash}; frames ${m.frames}`);
  await ctx.close(); await srv.close();
});
