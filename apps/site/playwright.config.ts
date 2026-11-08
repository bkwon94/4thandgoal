/**
 * Playwright config of the readability floor and the evidence run. The projects check the floor, prove its rules, and take shots.
 * Run the evidence project with pnpm evidence <slug>.
 */
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "e2e",
  // A static page loads fast, and two workers keep the run short on the two cores of the CI runner.
  workers: 2,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  reporter: "list",
  use: {
    ...devices["Desktop Chrome"],
    // The reveal starts each section at opacity 0. axe skips hidden text, so the check reads the page with no motion.
    reducedMotion: "reduce",
  },
  projects: [
    // The project "rules" proves each scan of the floor, and each rule of the evidence runner, on small real pages.
    { name: "rules", testMatch: ["floor-rules.spec.ts", "evidence-rules.spec.ts"] },
    // The project "floor" runs the floor on the static export in out/ of the current CLIENT, and checks the hero scene of
    // the latest week page, of a manager page, and of the rankings, midseason, home, and 404 pages there (ADR 0027).
    { name: "floor", testMatch: ["floor.spec.ts", "scene.spec.ts", "manager-scene.spec.ts", "page-scenes.spec.ts"] },
    // The evidence run shows the site as a reader sees it, with motion on. Its scroll pass shows each revealed section.
    { name: "evidence", testMatch: "evidence.spec.ts", use: { reducedMotion: "no-preference" } },
  ],
});
