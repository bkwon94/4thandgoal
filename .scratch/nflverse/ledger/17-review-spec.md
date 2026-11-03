# 17 — spec review

Verdict: one Important finding. The ticket boxes hold for a refetch that raises. A degraded refetch drops saved facts.

Diff: `e29e2b4..f553825` in the worktree `nflverse-17`. `uv run pytest -q tests/test_pipeline.py`: 56 passed.

## Critical

None.

## Important

1. `src/cornerstone/pipeline.py:183-187`. A degraded refetch replaces the saved extract for the build.
   - The fresh path sets a field to None when its source has no cache file and the download fails.
   - For a pbp failure, the fresh `drops` is None, but the saved `drops` holds data. The build then has no drop facts.
   - Before this diff, a rebuild of week 6 always had its drops. So this diff can remove facts from a rebuild.
   - This breaks the ticket line "the build continues with the facts it can make". The build can make the drop facts from the saved file.
   - The file itself stays as it was, so that half of the line holds.
   - Fix: when the refetch is degraded and `saved` is not None, fill each None field of `nfl` from `saved`, and merge the true flags of `saved.sources` in.
   - One-line form: `nfl = nfl.model_copy(update={k: getattr(saved, k) for k in saved.model_fields_set if getattr(nfl, k) is None})`, plus the `sources` merge.
   - Do not simply return `saved` on a degraded refetch. That loses `usage` and `next_games` when only one late source, such as ffopportunity, is down.
   - Add a test: an old extract plus a fetcher that returns `drops=None` keeps `drop_source == "nflverse"` and leaves the file bytes as they were.

## Minor

1. `src/cornerstone/pipeline.py:183`. The refetch replaces the whole extract, not only the absent keys. The ticket says "fetches that source again".
   - Real effect on week 6: `drops` and `gsis` match the saved file. `injuries` gains week 7 rows, 57 to 61 players, 19 changed.
   - The rows for weeks 1 to 6 match exactly, and the injury facts read only week N or earlier, so the week 6 page does not change.
   - Fix: none needed now. Note in the docstring that the refetch rewrites every key with the data of today.
2. `tests/test_pipeline.py:678`. Box 2, "every key fetches nothing", rests on `test_saved_extract_is_not_fetched_again`. That test is from before the diff. It still covers the box, because a fixture build saves every key.
   - Fix: none needed.

## Log line (check 3)

`src/cornerstone/pipeline.py:181` logs the absent keys: `nflverse.json lacks environment, expected, next_games, usage, so the build fetches the extract again`.
The line does not name the week. The raw directory sets the week, so the context is there, but the line alone does not show it.
Fix: add the week, for example `"week %d nflverse.json lacks %s, ..."`. This is Minor.

## Real-data check (check 4)

I copied `data/2026/week-06/raw/*.json` and `data/cache/nflverse/*` from the main repo to the scratchpad. I ran `_nflverse_for_week` with the real `played_teams`.

1. Fetcher that raises `OSError`: the file is unchanged by SHA-256. The result equals the saved extract. The log shows the refetch line, then `nflverse refetch failed, build goes on with the saved extract: disk gone`.
2. The real `nflverse_week` on the copied cache, with a fetch that raises `httpx.ConnectError`, so no network call and the stale cache serves:
   - All 7 sources true. The copied file is rewritten.
   - Keys gained: `environment`, `expected`, `next_games`, `usage`.
   - `usage` has 500 players, `environment` has 32 teams, `next_games` has 14 games, and `expected` is an `ExpectedPoints`.
   - `drops` and `gsis` equal the saved values. `injuries` differs only by week 7 rows, as in Minor 1.

The worktree file `data/2026/week-06/raw/nflverse.json` was never touched. `git status` is clean, so no `git checkout` was needed.

## Missing from the diff (check 5)

1. No test for a degraded refetch. See Important 1.
2. The ticket status stays `open`. This is correct until the merge.

## Re-review: fix round 1, `f553825..0ee436a`

Verdict: all three findings are ADDRESSED. The fix adds one new Important finding. `uv run pytest -q tests/test_pipeline.py`: 57 passed.

1. Important, degraded refetch lost saved drops: ADDRESSED. `_with_saved` at `src/cornerstone/pipeline.py:165` fills each None field from the saved extract. `test_a_refetch_with_a_source_down_keeps_the_saved_drops` covers it.
2. Minor, the log line lacked the week: ADDRESSED. `pipeline.py:194` logs `week 6 nflverse.json lacks environment, expected, next_games, usage, ...`. The test asserts the full line.
3. Minor, the docstring and the unused `bundle`: ADDRESSED. The docstring says that the refetch rewrites every key and why.

### Checks the coordinator asked for

- `_with_saved(fresh, saved)` with every fresh source true equals `fresh`. The result is the same for the plain saved week 6 extract and for a copy with `drops=None`. Real data: copied week 6 file and copied cache.
- A fetcher that raises: the copied `nflverse.json` is unchanged by SHA-256, and the result equals the saved extract.
- The worktree is clean. No data file changed, so no `git checkout` was needed.

### New Important

1. `src/cornerstone/pipeline.py:199-201`. The save check reads the merged flags, so a degraded refetch can be saved and frozen.
   - `_with_saved` sets a source true when the saved extract has it true. The check at line 201 then sees every source true and saves.
   - Some down sources do not give a None field. With no `db_playerids.csv`, `ffverse` is down, but `gsis` and `usage` are smaller dicts, not None. `_with_saved` cannot fill them.
   - Real data, a copied cache without `db_playerids.csv`: the merged `ffverse` flag is True, and the build saves the file. `usage` has 84 players, not 500. `gsis` has 36 entries, not 163.
   - The saved file now has every key, so later builds never refetch it. The next build with a good cache still has 84 usage players. The loss is permanent.
   - This also breaks the ticket line "a refetch that fails leaves the file as it was". The new test at `tests/test_pipeline.py:872` asserts a rewrite while FTN is down.
   - A pbp outage does not hit this bug, because `nflverse_snaps` is false when `usage` is None.
   - Fix: compute `complete = all(nfl.sources.get(key) for key in NFLVERSE_SOURCES)` before the `_with_saved` call at line 199. Save only when `complete` is true.
   - Then change the test at line 872 so that it asserts the file bytes stay as they were. Keep the assertion `drop_source == "nflverse"`.

## Re-review: fix round 2, `0ee436a..2ce5492`

Verdict: the round 1 Important is ADDRESSED. The probe fails one coordinator expectation, so one Important finding stays open. The fix diff breaks nothing new.

1. A degraded refetch was saved and frozen: ADDRESSED. `complete` at `src/cornerstone/pipeline.py:200` reads the fresh flags before `_with_saved`. The test asserts that the file text stays as it was.

### Probe: a copied cache without `db_playerids.csv`, with no network

- File: unchanged by SHA-256. This is correct.
- `gsis` in the build result: 36. The saved extract has 163. The coordinator expected 163. 127 saved ids are absent.
- `drops` in the build result: 3 players and 3 plays. The saved extract has 21 players and 27 plays. The coordinator expected the saved drops.
- `usage`: 84 players. A good cache gives 500.
- Merged `sources`: all true, `ffverse` too, but the ffverse source was down.

### Important (still open, from `0ee436a`, not new in this diff)

1. `src/cornerstone/pipeline.py:165-170`. `_with_saved` fills only None fields. A down ffverse source gives smaller dicts, not None.
   - So the build uses the cut `gsis` and `drops` in place of the saved ones. This build loses 24 of 27 drop plays.
   - This breaks "the build continues with the facts it can make", as in Important 1 of the first review.
   - The merged `ffverse` flag says true, so the build record hides the outage.
   - The case is rare. It needs no cached `db_playerids.csv` and a failed download. The file now stays safe, and the next build tries again.
   - Fix: when `complete` is false, prefer each non-None saved field and take fresh values only for the keys the saved file lacks.
   - One-line form: `update = {k: getattr(saved, k) for k in saved.model_fields_set if getattr(saved, k) is not None}`. Use it only on the degraded path.
   - For the sources, keep the saved flags for the keys the saved file has. Take the fresh flags for the new keys.
   - Add a test: a fetch with no ffverse file keeps the saved `drops` and `gsis`.

`git status` in the worktree is clean. No data file changed.

## Re-review: fix round 3, `2ce5492..f4117a6`

Verdict: the open Important is ADDRESSED. The fix diff adds no new breakage. `uv run pytest -q tests/test_pipeline.py`: 58 passed.

`_with_saved` at `src/cornerstone/pipeline.py:165` keeps every saved key and the saved flags. The refetch fills only the absent keys and flags. `test_a_refetch_without_ffverse_keeps_the_saved_keys` covers this.

### Probe 1: a copied cache without `db_playerids.csv`, with no network

- The file is unchanged by SHA-256.
- `gsis` has 163 entries. `drops` has 27 plays and equals the saved value. `injuries` equals the saved value.
- The `ffverse` flag is true, and every flag is true.
- The fresh keys arrive: `usage` has 84 players, `environment` has 32 teams, `next_games` has 14 games, and `expected` is present.

### Probe 2: the full copied cache, with no network

- `usage` has 500 players. `environment`, `next_games`, and `expected` are present.
- `gsis` has 163 entries. `drops` and `injuries` equal the saved values.
- The copied file is rewritten with all 8 keys. The saved keys keep their values, and the file loads equal to the build result.

### Minor (no action needed)

1. In probe 1, every flag is true, but `usage` has only 84 of 500 players, because the ffverse source was down. The build record does not show the cut. The file is not saved, so the next build tries again. Fix: none for this ticket. If it matters later, take the fresh `ffverse` flag when the refetch fills a key that depends on it.

The worktree is clean. No data file changed.
