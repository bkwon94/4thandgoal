/**
 * Playwright config of the readability floor. The project "rules" proves each scan of the floor on small real pages.
 * The project "floor" runs the floor on the static export in out/ of the current CLIENT.
 * The project "evidence" takes the shots of the acceptance tests of one feature. Run it with pnpm evidence <slug>.
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
    { name: "rules", testMatch: ["floor-rules.spec.ts", "evidence-rules.spec.ts"] },
    { name: "floor", testMatch: "floor.spec.ts" },
    // The evidence run shows the site as a reader sees it, with motion on. Its scroll pass shows each revealed section.
    { name: "evidence", testMatch: "evidence.spec.ts", use: { reducedMotion: "no-preference" } },
  ],
});
