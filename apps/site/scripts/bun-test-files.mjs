/**
 * The folders whose tests run on `bun test`, as paths from the repo root. Vitest runs each other test file.
 * The Vitest config skips these folders, and scripts/bun-test.mjs passes them to `bun test`, so each file has one runner.
 */

/* Each move ticket adds the folders of its tests here, after each file in them uses only `bun:test`. */
export const BUN_TEST_DIRS = [
  // One folder per line, so that the move tickets merge with no conflict.
  "apps/site/test",
  "packages/design/site",
];
