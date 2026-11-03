# Ticket 11 review: standards

Diff: `e29e2b4..ba200a5` on `nflverse-11`. Verdict: pass, with one minor item.

## Critical

None.

## Important

None.

## Minor

1. `tests/test_rubric.py:1220` and `tests/test_rubric.py:1227`: these are the only tests in the file that call a private function (`rubric._highest_value_player`). All other highest-value tests go through `grade` and read the "roster fit" or "standing" reason (lines 169-190, 251-268). A `grade` test is possible. Use a trade where the gain stays under the fit threshold, or give Jacobs to a seller that is out of the playoff race. Then the "standing" reason names the side that gets the highest-value player. Fix: add one `grade` test that shows the due-back player as the pick in a reason. Keep the direct tests, or drop them if the `grade` test covers both checks. The direct tests assert real values and are clear, so this item does not block the merge.

## Checked and clean

- Scope: the change touches only `_highest_value_player`, its import, its docstring, and the ticket checklist. Nothing outside the ticket.
- Import cycle: `adjusters.py` imports `cornerstone.rubric` only inside `if TYPE_CHECKING:` (line 39), with a comment that says why. No runtime cycle. This import was there before the change.
- `recent_points_per_game` has no other use in `rubric.py`, so its removal from the import is correct.
- Docstring stays true and follows STE: active voice, present tense, short sentences, no `-ing` verb. No comment removed.
- The comment at `tests/test_rubric.py:1213` is true: the fixture returns file has Jacobs back in week 7.
- Style: the `DIGGS` constant sits next to its tests, as `POLLARD` (line 166) and `DEEBO` (line 524) do. Code lines stay under 120 characters.
- Names: no "new", "improved", or "enhanced". No mock mode.
- Tests: both assert a specific player ID. Both fail if the fallback or the chart path picks the wrong player. Names say what they check.
