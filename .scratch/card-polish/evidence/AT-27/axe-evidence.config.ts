/**
 * Evidence only for AT-27 of card-polish: the Playwright config of axe-floor-evidence.spec.ts.
 * It uses the same browser as the floor project of playwright.config.ts, with reduced motion.
 */
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "e2e",
  testMatch: "axe-floor-evidence.spec.ts",
  workers: 1,
  reporter: "list",
  use: { ...devices["Desktop Chrome"], reducedMotion: "reduce" },
});
