/**
 * The folders and the files whose tests run on `bun test`, as paths from the repo root. Vitest runs each other test file.
 * The Vitest config skips these folders, and scripts/bun-test.mjs passes them to `bun test`, so each file has one runner.
 */

/* A folder that holds other test folders, such as apps/site/src, lists its test files one by one.
   Each move ticket adds the folders of its tests here, after each file in them uses only `bun:test`. */
export const BUN_TEST_DIRS = [
  // One folder per line, so that the move tickets merge with no conflict.
  "apps/site/test",
  "packages/design/site",
  "apps/site/scripts",
  "apps/site/src/lib",
  "apps/site/src/component-rule.test.ts",
  "apps/site/src/design-rule-raw-color.test.ts",
  "apps/site/src/design-rules.test.ts",
  "apps/site/src/grade-weights.test.ts",
  "apps/site/src/no-plate.test.ts",
  "apps/site/src/readme-rule.test.ts",
  "apps/site/src/reduced-motion-blocks.test.tsx",
  "apps/site/src/reduced-motion-site.test.tsx",
  "apps/site/src/reduced-motion.test.tsx",
  "apps/site/src/rule-report.test.ts",
  "apps/site/src/suppression-rule.test.ts",
  "apps/site/src/tracker-rule.test.ts",
  "apps/site/src/use-lines-rule.test.ts",
  "apps/site/src/value-rule.test.ts",
  "packages/analyzer/site/lib",
  "packages/analyzer/site/form",
  "packages/eggs/site",
  "packages/managers/site/page",
];
