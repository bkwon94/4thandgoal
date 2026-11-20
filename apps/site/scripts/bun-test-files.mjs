/**
 * The folders whose tests run on `bun test`, as paths from the repo root. Vitest runs each other test file.
 * The Vitest config skips these folders, and scripts/bun-test.mjs passes them to `bun test`, so each file has one runner.
 */

/* Each move ticket adds the folders of its tests here, after each file in them uses only `bun:test`. A folder that still
   holds a file on Vitest lists each moved file of it as its own entry instead. */
export const BUN_TEST_DIRS = [
  // One folder per line, so that the move tickets merge with no conflict.
  "apps/site/test",
  "packages/design/site",
  "apps/site/src/app/_routes/analyzer",
  "apps/site/src/app/_routes/ask",
  "apps/site/src/app/_routes/eggs",
  "apps/site/src/app/_routes/midseason",
  "apps/site/src/app/_routes/week",
  "apps/site/src/app/fonts",
  "apps/site/src/app/_routes/sim/menu.test.ts",
  "apps/site/src/app/_routes/sim/your-sim-page.test.tsx",
  "apps/site/src/app/brand-tokens.test.ts",
  "apps/site/src/app/callout.test.ts",
  "apps/site/src/app/front-door/answer-block.test.ts",
  "apps/site/src/app/front-door/ask-box.test.tsx",
  "apps/site/src/app/front-door/chat-turns.test.ts",
  "apps/site/src/app/front-door/comparison-block.test.tsx",
  "apps/site/src/app/front-door/feed-block.test.tsx",
  "apps/site/src/app/front-door/live-matchup.test.ts",
  "apps/site/src/app/front-door/nfl-game-card.test.tsx",
  "apps/site/src/app/front-door/passphrase-sheet.test.tsx",
  "apps/site/src/app/front-door/personal-stream.test.ts",
  "apps/site/src/app/front-door/suggestions-api.test.ts",
  "apps/site/src/app/front-door/team-sheet.test.tsx",
  "apps/site/src/app/front-door/text-block.test.tsx",
  "apps/site/src/app/front-door/thread.test.ts",
  "apps/site/src/app/front-door/tour-norcal.test.tsx",
  "apps/site/src/app/front-door/tour-replay.test.tsx",
  "apps/site/src/app/front-door/tour-store.test.ts",
  "apps/site/src/app/front-door/trade-steps.test.ts",
  "apps/site/src/app/home-flag.test.tsx",
  "apps/site/src/app/not-found.test.tsx",
  "apps/site/src/app/page-caps.test.tsx",
  "apps/site/src/app/page-matchup.test.tsx",
  "apps/site/src/app/page-recap.test.tsx",
  "apps/site/src/app/page-season.test.tsx",
  "apps/site/src/app/page-trade-card.test.tsx",
  "apps/site/src/app/page-trade.test.tsx",
  "apps/site/src/app/shell-props.test.ts",
  "apps/site/src/app/site-pages.test.tsx",
  "apps/site/src/app/viewport.test.ts",
];
