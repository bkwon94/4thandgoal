/**
 * The folders and files whose tests run on `bun test`, as paths from the repo root. Vitest runs each other test file.
 * The Vitest config skips these folders, and scripts/bun-test.mjs passes them to `bun test`, so each file has one runner.
 */

/* Each move ticket adds the folders of its tests here, after each file in them uses only `bun:test`. */
export const BUN_TEST_DIRS = [
  // One folder per line, so that the move tickets merge with no conflict.
  "apps/site/test",
  "packages/design/site",
  "packages/analyzer/site/lib",
  "packages/analyzer/site/form/analyze-result.test.tsx",
  "packages/analyzer/site/form/grade-bar.test.tsx",
  "packages/analyzer/site/form/passphrase-dialog.test.tsx",
  "packages/analyzer/site/form/sheet.test.tsx",
  "packages/analyzer/site/form/stage-lines-motion-off.test.tsx",
  "packages/analyzer/site/form/stage-lines.test.tsx",
  "packages/analyzer/site/form/team-picker.test.tsx",
  "packages/analyzer/site/form/trade-finder.test.tsx",
  "packages/analyzer/site/form/trade-on-stage.test.tsx",
  "packages/analyzer/site/form/use-request.test.ts",
  "packages/eggs/site",
  "packages/managers/site/page/best-adds.test.tsx",
  "packages/managers/site/page/grade-dial.test.tsx",
  "packages/managers/site/page/index-list.test.tsx",
  "packages/managers/site/page/manager-hero.test.tsx",
  "packages/managers/site/page/manager-scene.test.ts",
  "packages/managers/site/page/moves.test.tsx",
  "packages/managers/site/page/race-group.test.ts",
  "packages/managers/site/page/season-so-far.test.tsx",
  "packages/managers/site/page/top-performers.test.tsx",
];
