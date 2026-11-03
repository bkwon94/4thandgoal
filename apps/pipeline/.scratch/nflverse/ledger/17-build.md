# 17 — build report

Status: DONE_WITH_CONCERNS. Commit: `f553825` on branch `nflverse-17`. The commit is not pushed and not merged.

## What changed

`_nflverse_for_week` in `src/cornerstone/pipeline.py` now checks the saved `nflverse.json` file on load.

1. The required keys are the fields of `NflverseWeek`. The check compares them to `model_fields_set`. A key that the file does not hold loads as None, so only the set fields tell an old file from a new one. A fresh save writes every field, so a fresh file always passes the check.
2. When a key is absent and a fetcher exists, the build logs one INFO line: `nflverse.json lacks environment, expected, next_games, usage, so the build fetches the extract again`. Then it goes down the same fetch path as a week with no saved file.
3. A good refetch, with every source true, rewrites `nflverse.json`. A degraded refetch is not saved, as on the fresh path. The build then uses the refetched extract, as a build of today would.
4. A refetch that raises leaves the file as it was. The build then goes on with the saved extract and logs `nflverse refetch failed, build goes on with the saved extract`.
5. The build reads no other raw file again. The check is only in the nflverse load path.

## Files

- `src/cornerstone/pipeline.py`: `_nflverse_for_week` only. The diff adds 14 lines and removes 2.
- `tests/test_pipeline.py`: one helper and two tests.
- `.scratch/nflverse/issues/17-a-rebuild-of-a-saved-week-refetches-the-new-raw-files.md`: four boxes ticked. Status stays `open`.

I did not touch `cli.py` or `snapshot.py`. I did not touch `data/2026/week-06/raw/nflverse.json`.

## Tests added

- `_old_extract`: a helper. It cuts a saved extract down to `sources`, `gsis`, `drops`, and `injuries`, as in the saved week 6 file.
- `test_a_saved_extract_without_usage_is_fetched_again_and_rewritten`: the rewritten file holds `usage`, `expected`, and `next_games`. The `nflverse_stats_player` source is true. The log line names `usage`.
- `test_a_failed_refetch_keeps_the_saved_extract`: a fetcher that crashes leaves the file bytes as they were. The page builds, and `drop_source` stays `nflverse` from the saved drops.

The existing `test_saved_extract_is_not_fetched_again` covers the box for "every key fetches nothing". It uses a fetcher that raises, and it still passes.

Both new tests failed before the change and pass after it.

## Commands

- `uv run pytest -q`: `1038 passed, 9 deselected in 185.64s (0:03:05)`. Main has 1036, plus 2 new tests.
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` This is the same as main. The change adds none.

## Concerns

1. A degraded refetch returns the fresh extract, not the saved one. Example: the play by play is down at the time of the rebuild. Then the fresh extract has `drops` None, and the saved drops are not used for that build. The file stays as it was, so the next build tries again. This matches the fresh path. To keep the saved facts, merge the saved and fresh extracts. I chose not to, to keep the change small.
2. A refetch of an old week reads the shared nflverse cache. A cached file older than `CACHE_MAX_AGE_SECONDS` downloads again, so a real week 6 rebuild makes network calls. I did not run a real week 6 rebuild.
3. If a later ticket adds a field to `NflverseWeek`, every saved extract refetches once on its next rebuild. That is the purpose of the rule, but the reviewer must know about it.

## Fix round 1

Commit: `0ee436a`.

### Changes

1. Important: `_with_saved` in `src/cornerstone/pipeline.py` merges a refetch with the saved extract. Each None field of the refetch takes the saved value. A source is true if it is true in either extract. The build saves the merged extract only when every source is true, as before. A degraded refetch no longer loses the saved `drops`, and it keeps the fresh `usage`.
2. Minor: the log line now names the week: `week 6 nflverse.json lacks environment, expected, next_games, usage, so the build fetches the extract again`.
3. Minor: the dense condition is now two plain `if` blocks. The old order of checks stays the same: no fetcher returns the saved extract, and a full saved extract returns at once.
4. Minor: the docstring says that the refetch rewrites every key, why the past-week facts do not change, and that a field the refetch cannot fill keeps the saved value.
5. Minor: the test drops the unused `bundle` and asserts the full log line.

### Tests

- `test_a_refetch_with_a_source_down_keeps_the_saved_drops` is new. A fetch with no FTN file gives no drops but gives the usage. The build keeps `drop_source == "nflverse"`, the merged `nflverse_ftn` source is true, and the rewritten file holds the saved drops and the fresh usage.
- `test_a_saved_extract_without_usage_is_fetched_again_and_rewritten` asserts the full log line with the week.
- `test_a_failed_refetch_keeps_the_saved_extract` is unchanged and still passes.

Both changed tests failed before the fix and pass after it.

### Commands

- `uv run pytest -q tests/test_pipeline.py`: `57 passed in 18.56s`.
- `uv run pytest -q`: `1039 passed, 9 deselected in 159.37s (0:02:39)`.
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` This is the same as main.
- `git status --short`: clean after the commit. No data file changed.

### Concern

A merged extract can mix two dates: for example, saved drops and fresh injuries. Every source is still for the same week, so the facts agree.

## Fix round 2

Commit: `2ce5492`.

### Change

Important: `_nflverse_for_week` now computes `complete` from the flags of the fresh extract before `_with_saved` runs. The build saves only when the fresh extract is complete. Before, the save check read the merged flags, so the build could save a degraded refetch. That file then had every key, so no later build fetched it again. A comment above the check says why it reads the fresh flags.

### Test

`test_a_refetch_with_a_source_down_keeps_the_saved_drops` now asserts that the file content is unchanged after the degraded refetch. It still asserts `drop_source == "nflverse"` and the merged `nflverse_ftn` flag. It now also asserts `nflverse_snaps` is true, so the build uses the fresh usage. The test failed before the fix and passes after it.

### Commands

- `uv run pytest -q tests/test_pipeline.py`: `57 passed in 19.30s`.
- `uv run pytest -q`: `1039 passed, 9 deselected in 154.35s (0:02:34)`.
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` This is the same as main.
- `git status --short`: clean after the commit. No data file changed.

## Fix round 3

Commit: `f4117a6`.

### Change

Important: `_with_saved` now applies the final rule. The None-fill and the merge of the true flags are gone.

1. The saved value wins for every key the file holds.
2. The refetch fills only the keys the file lacks.
3. The flags of the saved file win. The fresh flags cover only the flags the saved file lacks. The flags of the old file are `nflverse_pbp`, `nflverse_ftn`, `nflverse_injuries`, and `ffverse`, so they match its keys.

The file is saved only when the fresh extract is complete, as in round 2. The docstring of `_nflverse_for_week` now says that the refetch fills only the absent keys. It no longer says that the refetch rewrites every key.

### Tests

- `test_a_refetch_without_ffverse_keeps_the_saved_keys` is new. It calls `_nflverse_for_week` directly with no `db_playerids.csv`, then checks:
  - `gsis` and `drops` equal the full saved values, and the `ffverse` flag is true from the saved file.
  - The fresh keys arrive: `usage` is `{}` in the fixture without the ID map, `environment` has rows, and `nflverse_snaps` is true.
  - The file content is unchanged.

  It failed before the fix: `gsis` was the smaller dict.
- The round 1 test, `test_a_refetch_with_a_source_down_keeps_the_saved_drops`, stays and passes.
- The `cornerstone.pipeline` import line in the test file is wrapped to stay under 120 characters.

### Commands

- `uv run pytest -q tests/test_pipeline.py`: `58 passed`.
- `uv run pytest -q`: `1040 passed, 9 deselected in 152.91s (0:02:32)`.
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` This is the same as main.
- `git status --short`: clean after the commit. No data file changed.

### Concern

In the fixture, `usage` is empty without the ID map. So the new test shows that the fresh key arrives, but not that it has rows. The round 1 test covers a refetch with usage rows.
