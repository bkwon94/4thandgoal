# Final review wave: build report

Branch `known-games-final`, base main `5561b8c`. One commit holds all five items.

## Item 1. The cache key misses three inputs (Important)

What changed in `src/cornerstone_api/cache.py`:

- `_content_hash` adds `known_games`, the `model_dump()` of the stamp block, or None.
- `_content_hash` adds `stats_stale`, true when `"stats"` is in `snapshot.stale`.
- Each roster adds `week_n_wopr`: the week `stats_through` WOPR row of each rostered player.
- The new helper `_week_n_wopr` gives these rows. It is empty when `stats_through <= completed_through` or with no WOPR file.
- The docstring names the three new inputs and why each goes in.
- `DOCUMENT_VERSION` is now 7.

Tests in `tests/test_api.py`. Each checks the grade key and the finder key:

- `test_the_cache_key_changes_with_the_known_games_block`: a changed pending count, and no block, each give a new key.
- `test_the_cache_key_changes_when_the_stats_are_stale`: `"stats"` in `stale` gives a new key.
- `test_the_cache_key_changes_with_a_week_n_wopr_row_of_a_rostered_player`: a week 6 row gives a new key. A week 6 row of a player on neither roster keeps the key.
- `test_the_document_version_is_6` is now `test_the_document_version_is_7`.

RED: all four failed. Each key test failed with two equal hashes, for example
`AssertionError: assert '8342d550...' != '8342d550...'`. The version test failed with `6 == 7`.
GREEN: `tests/test_api.py` gave 116 passed.

## Item 2. The trade fact claims one bound (Minor)

`_week_fact` in `src/cornerstone/trade_facts.py` names both bounds when `stats_through > completed_through`:
"Player stats run through the known games of week 6. The record runs through week 5."
When the bounds are equal, the sentence stays "Every stat runs through week N."

The test `test_the_player_stat_readers_of_a_known_games_week_read_its_games` checks the two-bound text.
It also checks that the text has no "Every stat". The test also checks the equal-bound sentence on `at_week_5`.

RED: `AssertionError: assert 'Player stats run through the known games of week 6. The record runs through week 5.' in 'The trade is in week 6 of the 2026 season. Every stat runs through week 6.'`
GREEN: `tests/test_rubric.py` gave 156 passed.

## Item 3. The CLI first line (Minor)

`_print_as_of` in `src/cornerstone/cli.py` prints `completed_through` when the known-games block has games.
Otherwise it prints `stats_through`. On the fixture game day the two lines now read
"Stats through week 5." and then "Known games of week 6: 14 read, ...".

The test `test_analyze_without_week_grades_the_live_snapshot_and_prints_the_as_of_line` now expects "Stats through week 5.".

RED: the assertion failed because the output had "Stats through week 6.".
GREEN: `tests/test_cli.py` gave 27 passed.

## Item 4. A guard test for the injury report bound (Minor)

The new test is `test_the_injury_report_of_a_known_games_week_ends_at_the_completed_week` in `tests/test_rubric.py`.
It uses `known_snap` with bounds 6 and 5. Chris Olave gets report rows in weeks 3, 4, and 6.
The injury step must be 0, and the fact sheet must say "in 2 weeks".

The test passes on the present code, as a guard must. RED evidence is from two temporary mutations:

- `adjusters._report_weeks` read through `stats_through`: `AssertionError: assert -1 == 0`.
- `trade_facts._report_weeks` read through `stats_through`: the fact said "in 3 weeks", so the assertion failed.

I restored each file with `git checkout` after each run. GREEN: 1 passed.

## Item 5. A grade-level WOPR test (Minor)

The new test is `test_the_trend_step_reads_a_week_n_wopr_row_when_the_file_has_it_and_ends_a_week_before_without_it`.
It is in `tests/test_rubric.py` and goes through `grade`. Mike Evans on roster 1 and Wan'Dale Robinson on roster 2 are WRs.
Both played week 6 with flat snap and target shares in `known_snap`. I picked them with a scan of the fixture.

- With a week 6 row, Evans reads "WOPR 55, up, over weeks 5 and 6."
- Without it, Evans reads "WOPR 55, up, over weeks 4 and 5."
- Roster 2 gets the same step, 1, in both.

The test passes on the present code. RED evidence is from two temporary mutations of `_wopr`:

- The window drops week N rows: the reason became the red-zone sentence, so "over weeks 5 and 6" failed.
- The window always ends at `stats_through`: the window had a week with no row, so "over weeks 4 and 5" failed.

I restored the file after each run. GREEN: 1 passed.

## Suite and lint

- `uv run pytest -q`: 1146 passed, 9 deselected.
- `uv run ruff check src tests`: no output, exit 0.

## Concerns

1. In both mutations of item 5 the red-zone tie break also gives step 1. So the step-equality assertion alone cannot catch a broken window. The reason assertions catch it.
2. The `known_games` key input holds the full block, with `games` and `in_progress`. A new game read without a rostered player changes the key too. The document shows these counts, so this is right, but the hit rate on a game day goes down.
3. `_week_n_wopr` reads the rows of all players, and the roster filter is in `_content_hash`. This matches `_week_n_lines`.
