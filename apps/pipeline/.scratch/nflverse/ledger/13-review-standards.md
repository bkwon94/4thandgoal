# 13 review: standards

Verdict: no Critical, no Important. Two Minor.

## Critical
none

## Important
none

## Minor
- tests/test_api.py (return week and projection tests): the player ids "7569" and "10236" must sit on roster 4 or 12.
  The build report says the tests do not depend on fixture content, but they do. Fix: pick the id from `snapshot.rosters[4]`.
- src/cornerstone_api/cache.py (`_content_hash`): the two comprehensions wrap in a hanging style. It is legal but dense.
  Fix: none needed. Optional: name `roster = snapshot.rosters[roster_id]` for easy reading.

## Checks that pass
- Change is minimal. Only `_content_hash`, its docstring, three tests, and the ticket boxes changed. No comment removed.
- Docstring stays true: it names the week rows and says why. Sentences are short, active, present tense.
- No "new" or "improved" names. No mock mode. Lines are 120 characters or fewer.
- Tests assert real inequality and equality on both the analyze key and the finder key.
- JSON safety: `returns` is `dict[str, int]`. `projections_ahead` is `dict[str, dict[int, float]] | None`. The `None` case maps to `{}`.
  All values are int or float. No Decimal, no date. The inner int keys go through `json.dumps(sort_keys=True)` as strings, like the int roster keys.
