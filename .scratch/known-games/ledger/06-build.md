# 06 build: the cache key hashes the week N stat lines

Status: DONE. Branch `known-games-06`, base `67f1a4d`. Not pushed.

## What I built
- `src/cornerstone_api/cache.py`: `STAT_FIELDS` (the seven fields) and `_week_n_lines`.
- `_week_n_lines` reads the week at `stats_through` when `stats_through` is past `completed_through`. That is a known-games week. Else it returns nothing.
- It cuts each line to the seven fields and drops a player with no field. No lines and empty lines give one key.
- `_content_hash` adds `week_n_lines` per roster, for the rostered players only. The analyze key and the finder key share it.
- `DOCUMENT_VERSION` is 6.

## Files changed
- `src/cornerstone_api/cache.py`
- `tests/test_api.py`: six new tests. No earlier test pinned the version, so `test_the_document_version_is_6` is new.

## TDD evidence
- RED: 3 failed, 3 passed. The rostered-line test and the empty-line test saw equal keys. The version test saw 5.
- The 3 passing tests (outside player, unread field, no known games) guard the old behavior.
- GREEN: 6 passed after the change.

## Suite and lint
- `uv run pytest -q`: 1115 passed, 9 deselected.
- `uv run ruff check src tests`: see the reply below. It printed no finding.

## Self-review
- The cache never sees the trade week, so the known-games test is `stats_through > completed_through`.
- The check `stats_through in weeks` guards a hand-built snapshot.

## Concerns
None.
