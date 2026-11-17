/**
 * The Playwright config of the analyzer-stage evidence scripts, outside the product projects.
 * It runs the specs of the scratch folder against the real export and the real local API.
 */
import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: process.env.EV_TESTS!,
  workers: 1,
  reporter: "list",
  timeout: 0,
  use: { ...devices["Desktop Chrome"], reducedMotion: "no-preference" },
});
