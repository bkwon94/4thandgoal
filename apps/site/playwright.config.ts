/**
 * Playwright config of the readability floor and the evidence run. The projects check the floor, prove its rules, and take shots.
 * Run the evidence project with pnpm evidence <slug>.
 */
import { defineConfig, devices } from "@playwright/test";

// The specs of the floor. The projects "floor" and "floor-timing" split them by the tag @timing.
const FLOOR_SPECS = ["floor.spec.ts", "scene.spec.ts", "manager-scene.spec.ts", "page-scenes.spec.ts", "front-door*.spec.ts", "analyzer-stage.spec.ts", "menu-sheet.spec.ts"];

export default defineConfig({
  testDir: "e2e",
  // A static page loads fast. The CI runner of a public repo has four cores, so CI runs four workers.
  // A local run keeps two workers, because agents run the checks in many worktrees at once.
  workers: process.env.CI ? 4 : 2,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  reporter: "list",
  use: {
    ...devices["Desktop Chrome"],
    // The reveal starts each section at opacity 0. axe skips hidden text, so the check reads the page with no motion.
    reducedMotion: "reduce",
  },
  projects: [
    // The project "rules" proves each scan of the floor, and each rule of the evidence runner, the smoke run, and the start of
    // its local API, on small real pages.
    { name: "rules", testMatch: ["floor-rules.spec.ts", "evidence-rules.spec.ts", "smoke-rules.spec.ts", "local-api-rules.spec.ts"] },
    // The project "floor" runs the floor on the static export in out/ of the current CLIENT, and checks the hero scene of
    // the latest week page, of a manager page, and of the home and 404 pages there, and the static heroes (ADR 0027). It also checks
    // the layout of the front door, and the idle mesh of the analyzer hero. It skips the tests tagged @timing, which the
    // project "floor-timing" runs.
    {
      name: "floor",
      testMatch: FLOOR_SPECS,
      grepInvert: /@timing/,
    },
    // The project "floor-timing" runs the tests of the floor that assert a wall-time limit. Run it after the project "floor",
    // with one worker (scripts/check-floor.mjs does both). CPU load from other workers delays a frame, so a limit of 100 ms
    // fails in a parallel run and holds in a run alone.
    {
      name: "floor-timing",
      testMatch: FLOOR_SPECS,
      grep: /@timing/,
      fullyParallel: false,
    },
    // The project "grade-bar" builds the export of NorCal, the client with the finder on, and checks the place of the grade bar.
    // It also checks the headshot frames of the analyzer result on the same export.
    { name: "grade-bar", testMatch: ["grade-bar.spec.ts", "analyze-headshot.spec.ts"] },
    // The evidence run shows the site as a reader sees it, with motion on. Its scroll pass shows each revealed section.
    { name: "evidence", testMatch: "evidence.spec.ts", use: { reducedMotion: "no-preference" } },
    // The smoke run of the verify skill drives each picked flow in WebKit and Chromium, with motion on, against its own
    // local API on a free port. It launches its own two browsers. Run it with pnpm smoke --out <dir>.
    { name: "smoke", testMatch: "smoke.spec.ts", use: { reducedMotion: "no-preference" } },
    // The project "open-card" checks find-in-page and the frame rate of the Open card on the export of cpc, with motion on.
    // It records evidence for ADR 0028, so no check of CI runs it.
    { name: "open-card", testMatch: "open-card.spec.ts", use: { reducedMotion: "no-preference" } },
    // The end-to-end run of the egg hunt against the local API. It starts no API, unlike the smoke run and the evidence
    // round, so run make -C apps/api api-evidence first, with its default port and origin.
    // One worker, because the two widths claim the same test egg one after the other.
    { name: "eggs", testMatch: "eggs.spec.ts", fullyParallel: false },
  ],
});
