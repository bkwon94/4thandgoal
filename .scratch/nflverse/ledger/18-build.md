# 18 — build report

Status: DONE_WITH_CONCERNS. Branch `nflverse-18`, commit `6e9b528`. Not pushed, not merged.

## What changed

- `src/cornerstone/cli.py`: `_SOURCE_NAMES` now comes from `REFRESHED_SOURCES`. Each key is the plain name with
  underscores. "points allowed" goes in after the depth charts, because it comes from the history and not from a
  refresh. The present line builds from `_SOURCE_NAMES`. It leaves out the id map, because the id map only joins
  ids. A missing id map still shows in the missing line.
- `src/cornerstone/slow_sources.py`: `missing` now names `expected_points` when `expected` is None. It names
  `player_weeks` when `wopr` is None. The two comments and the module docstring that said "not in `missing`" were
  false after the change, so they now say the new rule.
- `src/cornerstone/snapshot.py`: `SLOW_SOURCES` gains `expected_points` and `player_weeks`. A snapshot with no
  loader result names all seven as missing.

The injuries already flowed through the `sources` dict and `missing`. Only the line did not print it. The expected
points and the WOPR load outside that dict, so the loader adds them to `missing` by the names of their files.

## Tests

- `tests/test_cli.py`: new `test_analyze_names_the_one_source_the_cache_lacks` removes `ep_weekly_2026.csv` and
  checks "Sources missing: expected points.". New `test_the_source_names_are_the_names_of_the_refreshed_sources`
  checks every name of `REFRESHED_SOURCES` is in `_SOURCE_NAMES`.
- Changed assertions (see concerns): two in `tests/test_cli.py`, ten in `tests/test_slow_sources.py`, two in
  `tests/test_snapshot.py`. Two loader test names changed from `misses_nothing` to `names_it_as_missing`.

Command: `uv run pytest -q`. Last line: `1038 passed, 9 deselected in 170.22s (0:02:50)`.

Ruff: `uv run ruff check --line-length 120 src tests` gives 135 errors. Main gives 135. None added.

## Real-data check

`make analyze A=11:5850 B=3:6806 ASKER=3`:

    Sources: schedules, depth charts, points allowed, injuries, expected points, player weeks.

## API

`src/cornerstone_api/analyzer.py` sends `list(snapshot.missing)` in the `missing` field of both the analyze and the
find documents. That list now also holds `expected_points` and `player_weeks` when those files are absent. The keys
use underscores, as `depth_charts` and `id_map` do. `stale` does not change: it still comes from the refresh in
`live.py` and uses the plain names. The site front end is not in this repo. Check that it shows or ignores the two
new keys well.

## Concerns

1. The ticket box "Every existing cli test passes unchanged" cannot hold, so it is not ticked. Two cli tests pinned
   the old line. `test_analyze_names_the_sources_it_has_from_the_cache` has every file, so its line is now the full
   line of box 1. `test_analyze_prints_the_breakdown_per_side_with_no_trade_value` has no cache, so the missing line
   now also names injuries, expected points, and player weeks. I changed the two assertions to the new lines.
2. Ten loader assertions and two snapshot assertions pinned the old rule that an absent expected points file or
   weekly player file misses nothing. The ticket changes that rule, so I changed them.
3. `expected` is None also when the league scoring or the id map is absent. Those cases now show
   "expected points" as missing too. That is true, because the grade did not read the data.
4. The print order depends on the order of `REFRESHED_SOURCES`: points allowed goes in at index 2. A change of that
   order changes the line. The cli test with every file catches it.

## Fix round 1

Commit `f851530`.

- Important 1: `_SOURCE_NAMES` in `src/cornerstone/cli.py` is now a plain dict of the seven keys and names in
  print order. `cli.py` no longer imports `REFRESHED_SOURCES`. `_JOIN_ONLY` stays, defined next to the dict.
- Important 2: `test_the_source_names_are_the_names_of_the_refreshed_sources` in `tests/test_cli.py` now asserts
  `set(cli._SOURCE_NAMES) == set(SLOW_SOURCES)`. It also asserts every name of `REFRESHED_SOURCES` is a value.
- Minor 3: the comment on the print order no longer gives a false cause. It says the first three keep the order of
  the old line.
- Minor 4: renamed `test_load_slow_sources_gives_every_source` to `..._gives_every_source_in_the_cache`. Renamed
  `test_slow_sources_fill_the_snapshot_and_none_stay_missing` to
  `..._and_only_the_files_not_in_the_cache_stay_missing`.
- Minor 5: the expected points test and the WOPR test in `tests/test_slow_sources.py` now assert the exact list:
  `NOT_IN_CACHE`, and `["id_map", *NOT_IN_CACHE]` after the unlink of the id map.

Covering tests: `tests/test_cli.py`, `tests/test_slow_sources.py`, `tests/test_snapshot.py` give `47 passed`.

Command: `uv run pytest -q`. Last line: `1038 passed, 9 deselected in 154.74s (0:02:34)`.

Ruff: `Found 135 errors.` Unchanged.

Real data, unchanged: `Sources: schedules, depth charts, points allowed, injuries, expected points, player weeks.`
