# 18 — spec review

Verdict: no Critical and no Important findings. Three Minor findings are below. Branch `nflverse-18`, commit `6e9b528`, base `e29e2b4`.

## Critical

None.

## Important

None.

## Minor

1. `tests/test_snapshot.py:67` — the test name says "none stay missing", but the test now checks two missing names. Fix: rename it to `..._and_only_the_absent_files_stay_missing`.
2. `tests/test_slow_sources.py:24` — the name `test_load_slow_sources_gives_every_source` now checks `missing == NOT_IN_CACHE`. Fix: rename it to say "every source in the cache".
3. `tests/test_slow_sources.py:86` and `:103` — the checks changed from `missing == []` to `"<key>" in missing`, which is weaker. Fix: assert the full list, for example `== ["expected_points", "player_weeks"]`.

## Checklist

- Box 1 holds. `tests/test_cli.py` `test_analyze_names_the_sources_it_has_from_the_cache` asserts the full line. The code is `src/cornerstone/cli.py` `_sources_line`.
- Box 2 holds. `tests/test_cli.py` `test_analyze_names_the_one_source_the_cache_lacks` removes `ep_weekly_2026.csv` and asserts "Sources missing: expected points.".
- Box 3 is unticked, as agreed. Two cli asserts changed to the new line. The loader and snapshot asserts changed only to the rule the ticket reverses. No test changed meaning past that rule.
- The ticket asks that the snapshot mark each of the three as missing. `injuries` was already in `SLOW_SOURCES`. `snapshot.py:26` adds the other two. Nothing in the ticket is absent from the diff.
- `uv run pytest -q tests/test_cli.py tests/test_slow_sources.py tests/test_snapshot.py tests/test_api.py`: `146 passed`.

## API and site

- `src/cornerstone_api/analyzer.py:158` and `:237` send `list(snapshot.missing)`. The list can now hold `expected_points` and `player_weeks`.
- The site at `/Users/brian.kwon/repos/cpcfantasyfootball` types `missing` and `stale` as `string[]` in `src/lib/analyze-types.ts:83-84` and `:109-110`. No component reads either field. The site does not show a raw key, has no fixed table, and cannot crash on the new keys.
- No other code in `src/` reads `Snapshot.missing` except `cli.py` and `snapshot.py`.

## Cache

No version bump. `DOCUMENT_VERSION` (`src/cornerstone_api/cache.py:22`) guards the shape and the grade rules. The `missing` field keeps its shape, a list of strings. No grade rule changed. The cache key does not hold `missing`. An old document on Fly can under-report `missing`, but the site never shows the field.

## Real-data check

`make analyze A=11:5850 B=3:6806 ASKER=3`:

    Sources: schedules, depth charts, points allowed, injuries, expected points, player weeks.

A temp copy of the cache with `cornerstone.live.nflverse_cache_dir` patched to it and `_refresh` patched to do nothing:

- `stats_player_week_2026.csv.gz` removed: `Sources missing: player weeks.`
- `ep_weekly_2026.csv` removed: `Sources missing: expected points.`
