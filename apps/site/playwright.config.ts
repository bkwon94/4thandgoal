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
    // the latest week page, of a manager page, and of the home and 404 pages there, and the static heroes (ADR 0027). It also checks
    // the layout of the front door.
    { name: "floor", testMatch: ["floor.spec.ts", "scene.spec.ts", "manager-scene.spec.ts", "page-scenes.spec.ts", "front-door.spec.ts"] },
    // The evidence run shows the site as a reader sees it, with motion on. Its scroll pass shows each revealed section.
    { name: "evidence", testMatch: "evidence.spec.ts", use: { reducedMotion: "no-preference" } },
    // The project "open-card" checks find-in-page and the frame rate of the Open card on the export of cpc, with motion on.
    // It records evidence for ADR 0028, so no check of CI runs it.
    { name: "open-card", testMatch: "open-card.spec.ts", use: { reducedMotion: "no-preference" } },
    // The end-to-end run of the egg hunt against the local API. Run make -C apps/api api-evidence first.
    // One worker, because the two widths claim the same test egg one after the other.
    { name: "eggs", testMatch: "eggs.spec.ts", fullyParallel: false },
  ],
});
