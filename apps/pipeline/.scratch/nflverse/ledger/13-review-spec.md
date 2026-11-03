# 13 review — spec compliance

Verdict: PASS with one Important item and one Minor item. No Critical item.
Diff: `e29e2b4..2461b9a` on `nflverse-13`.

## Checklist

1. A return week change gives a new key. Met by `test_the_cache_key_changes_with_a_rostered_return_week`, `tests/test_api.py:531`. The test checks the analyze key and the finder key.
2. A projection change gives a new key. Met by `test_the_cache_key_changes_with_a_rostered_projection_ahead`, `tests/test_api.py:541`. The test checks both keys.
3. A player on neither roster leaves the key the same. Met by `test_the_cache_key_ignores_a_player_on_neither_roster`, `tests/test_api.py:550`.
4. The existing cache tests pass unchanged. `uv run pytest -q tests/test_api.py -k cache_key` gives `6 passed`. The diff edits no existing test.

## Key stability (no Critical)

The key is stable when nothing real changes.

- The fetch time `as_of.rosters_fetched` is not in the key. `cache_key` hashes only `chart_week` and `stats_through` from `as_of`.
- `json.dumps(..., sort_keys=True)` fixes the dict order at each depth. The int week keys all have one type, so the sort never mixes types.
- The floats come from `float(points)` on the parsed Sleeper JSON. The same JSON gives the same float and the same `repr`. No arithmetic touches the values before the hash.
- A second process with `PYTHONHASHSEED=7` gives the same key, so the on-disk cache survives a restart.

## Real-data check, `data/2026/week-06/raw/`

The script reads the saved files two times with `load_raw` and `build_snapshot`, `trade_week=7`. The fetch times differ by one second. The trade is roster 11 (gives `5850`, the one player in `returns.json`) with roster 12. 27 rostered players have projection rows.

| Build | `cache_key` | `finder_cache_key` |
| --- | --- | --- |
| First | `f5fa211c` | `98bb644d` |
| Second, one second later | `f5fa211c` | `98bb644d` |
| Copy of `returns.json` with `5850` moved from week 7 to week 8 | `ca27eb02` | `012f8a9c` |

The same files give the same keys. One moved return week changes both keys.

## Important

- `src/cornerstone_api/cache.py:61` — The key hashes every week of projection for every rostered player. That is about 27 players and 12 weeks on the live path. The grade reads the rows only for a due-back player: `lineup_value` calls `projection_ahead` only when `_due_back` is true (`src/cornerstone/adjusters.py:118`). Sleeper updates projections at least daily, and more often near game day. The current-week row comes from `raw["projections"]`, which `fetch_live_raw` fetches on every request, outside the five-minute cache. So the key changes each time Sleeper moves any projection of any of the 27 players, and a hit lives for hours at most. Recommendation: hash the rows only of rostered players with an entry in `snapshot.returns`, from the return week through `LAST_REGULAR_WEEK`. That is exactly the set of rows `projection_ahead` can read. Reason: the hash then changes only when a value the grade reads changes, and most rosters have no player in the returns file. Do not hash the rounded mean: the key then copies the adjuster logic, and a change to that logic can drift from the key. This is a judgment, not a block. Fix: filter line 61 to `player in snapshot.returns` and to weeks `>= snapshot.returns[player]`.

## Minor

- `src/cornerstone_api/cache.py:54` — `snapshot.projections_ahead or {}` gives the same key for `None` and for a dict with no rostered row. The grade differs: with `None`, a due-back player keeps his recent points; with a dict, he counts for 0. The live path always sets the projections, so the collision needs a saved week without `projections_ahead.json`. Fix: put `"has_projections": snapshot.projections_ahead is not None` in the content of each roster.

## Missing from the diff

Nothing. The ticket asks for the return week and the projections ahead in `_content_hash`, for the finder key to share them, and for four tests. The diff has all of them.

## Re-review, fix commit `6f88a56`

Verdict: all three findings ADDRESSED. The fix diff `2461b9a..6f88a56` breaks nothing new.

1. Important: ADDRESSED. `_rows_read` (`src/cornerstone_api/cache.py:74`) keeps only the weeks from the return week through `LAST_REGULAR_WEEK`. Line 64 sends rows only for rostered players in `snapshot.returns`. This is the same range that `projection_ahead` reads (`src/cornerstone/adjusters.py:106`). The key hashes no mean.
2. Minor (`None` against an empty file): ADDRESSED. Line 70 adds `has_projections_ahead`. `test_the_cache_key_tells_no_projections_file_from_no_rostered_rows` covers it.
3. Minor (standards): ADDRESSED. The tests take the id from `snapshot.rosters[4][0]`. Two new tests cover the rows that the grade never reads and the `None` split. `uv run pytest -q tests/test_api.py -k cache_key` gives `8 passed`.

### Real-data check, `data/2026/week-06/raw/`, again

| Build | `cache_key` | `finder_cache_key` |
| --- | --- | --- |
| First | `0c752c40` | `aeb68733` |
| Second, one second later | `0c752c40` | `aeb68733` |
| `5850` return moved from week 7 to week 8 | `9dfd6fda` | `3f684b24` |
| Week 14 projection +3.0 for `11647`, rostered, not due back | `0c752c40` (same) | same |
| Week 14 projection +3.0 for `5850`, due back | `62edbcc8` (changed) | — |

The key is stable. A row the grade cannot read keeps the hit. A row the grade reads clears it.

### New findings

None. The builder's concern holds as a known cost: a player whose return week has passed still has rows in the key. That can only cause an extra miss, never a stale hit.
