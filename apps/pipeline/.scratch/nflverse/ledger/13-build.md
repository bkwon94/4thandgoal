# 13 build — the cache key hashes the projections and the returns

Status: DONE. Branch `nflverse-13`, commit `2461b9a`. No push, no merge.

## What changed

- `src/cornerstone_api/cache.py`: `_content_hash` now puts two more fields in each roster entry.
  - `returns`: the return week of each rostered player that has a row in `snapshot.returns`.
  - `projections_ahead`: the rows of each rostered player in `snapshot.projections_ahead`. A `None` field counts as empty.
  - The docstring says why: a new injuries file lands daily, and `DOCUMENT_VERSION` covers a deploy only.
- `cache_key` and `finder_cache_key` share `_content_hash`, so both keys gain the rows. No other code changed.
- The hash stays deterministic. `json.dumps(..., sort_keys=True)` sorts the keys. The int week keys become JSON strings. The values are ints and floats.
- The ticket file: all four boxes ticked. Status stays `open`.

## DOCUMENT_VERSION

Not bumped. The stored document shape and the grade rules do not change. The key content changes, so every old key misses once after the deploy anyway. A bump would add nothing.

## Tests added (`tests/test_api.py`, after the document version test)

- `test_the_cache_key_changes_with_a_rostered_return_week`: checks the analyze key and the finder key.
- `test_the_cache_key_changes_with_a_rostered_projection_ahead`: checks both keys.
- `test_the_cache_key_ignores_a_player_on_neither_roster`: checks both keys.
- Two helpers: `_with_week_rows` and `_outside_player`.

The tests set `returns` and `projections_ahead` with `model_copy`, so they do not depend on fixture content. Before the fix, the first two tests failed and the third passed.

## Checks

- `uv run pytest -q`: `1039 passed, 9 deselected in 184.08s (0:03:04)`. That is 1036 plus 3.
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` Same as main. `cache.py` has none.

## Concerns

- None blocking.
- The key holds every projection ahead of every rostered player, including weeks the grade may not read. Any change in those rows clears the cache. This matches the ticket text.

## Fix round 1

Commit `6f88a56` on `nflverse-13`. No push, no merge.

### What changed

- Important, `cache.py`: the key now holds projection rows only for rostered players in `snapshot.returns`. It keeps only the weeks from the return week through `LAST_REGULAR_WEEK`. These are the rows that `projection_ahead` reads. A new helper `_rows_read` does the filter. The key does not hash the mean, so it does not copy the adjuster logic.
- The return week of every rostered player stays in the hash.
- Minor, `cache.py`: the content now holds a `has_projections_ahead` flag. So `None` and an empty file give two keys.
- Minor, `tests/test_api.py`: the tests take the player id from `snapshot.rosters[4]`. No test hard-codes an id now.

### Tests

- `test_the_cache_key_changes_with_a_rostered_return_week`: changed to use the roster id.
- `test_the_cache_key_changes_with_a_projection_ahead_of_a_rostered_player_due_back`: replaces the old projection test.
- `test_the_cache_key_ignores_the_projection_rows_the_grade_never_reads`: new. It covers a player not due back, and a week before the return week.
- `test_the_cache_key_tells_no_projections_file_from_no_rostered_rows`: new.
- `test_the_cache_key_ignores_a_player_on_neither_roster`: no change.
- Before the fix, the two new tests failed. After the fix, all of them pass.

### Checks

- `uv run pytest -q tests/test_api.py`: `104 passed in 60.19s (0:01:00)`.
- `uv run pytest -q`: `1041 passed, 9 deselected in 155.39s (0:02:35)`.
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` This is the same count as main.

### Concerns

- The key holds the rows of every player in `returns`, including a player whose return week has passed. `_due_back` may skip that player, so the key can miss a little more often than the grade needs. The key cannot miss a change that the grade reads.
