# Final site build

Item 1: known-games-segments.ts uses completed_through (fallback stats_through - 1) as the base when the block has games. Tests now use stats_through 7, completed_through 6, week 7 block. Fixture line is "Stats through week 5, plus 14 week 6 games · Usage pending for 8 games · Chart week 6 · rosters fetched ...". Added a test for the fallback.
Item 2: AsOfLine takes doc {as_of, stale}. A "stats" entry in stale adds "Week N stats not fetched" between the pending segments and "Chart week N". Both documents already carry stale, so the finder page passes it with no change. One new test pins it.
TDD: RED was 9 failing tests after the test edits (before the code change). GREEN: 33 files, 288 tests pass. pnpm typecheck passes.
Concern: the games=0 test now sets stats_through 6 to match the pipeline (no played game).
