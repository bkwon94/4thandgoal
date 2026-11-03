# Ticket 12 review: standards

Diff: `e29e2b4..f95732f` on `nflverse-12`.

## Critical

None.

## Important

None.

## Minor

1. `src/cornerstone/adjusters.py:384` uses single quotes inside the f-string: `named(snapshot, due_back, 'returns', 'return')`.
   The rest of the file passes double-quoted phrases to `named`, as at line 397.
   Fix: assign `names = named(snapshot, due_back, "returns", "return")` first, then use `f"after {names} in week {week}"`.
2. `src/cornerstone/adjusters.py:376` the docstring phrase "each player due back it gets who starts" is hard to parse.
   It also does not say that the week is the latest of the return weeks.
   Fix: "When the lineup gain comes: now, or after the players due back who start for the side return, in the latest week."
3. `tests/test_rubric.py:1161` covers one player due back only. No test pins the two-player text or the `max` week.
   Fix: add one test with two starters due back in weeks 9 and 10 that asserts "after A and B return in week 10".

## Checks that pass

- The change is the smallest that meets the ticket. Only `_standing` and one helper change. The seller text is untouched.
- `_gain_when` reuses `named` for one or many players. It reads `snapshot.returns[pid]` the same way as line 296.
- `_gain_when` reuses `_due_back`. No logic is duplicated.
- The two-player reason reads as one plain sentence: "the best lineup gains after A and B return in week N."
- No comment is removed. The `_standing` docstring stays true.
- No name has "new", "improved", or "enhanced". No mock mode.
- The test asserts the full reason string and the step. The test name says what it checks.
- The healthy case keeps the existing test `test_a_contender_steps_up_for_a_lineup_gain_now` unchanged.
- The wrapped `Adjuster(...)` call matches the continuation style at lines 316-317.

## Re-review of the fix pass (f95732f..HEAD)

1. Minor 1 (single quotes in the f-string): ADDRESSED. `returns = named(snapshot, due_back, "returns", "return")` comes first. Double quotes match the file.
2. Minor 2 (docstring): ADDRESSED. The text now says the week is the latest return week of the starters due back.
   Style nit: the first line "When the side's lineup gain comes." is a fragment, not a sentence. Not blocking.
3. Minor 3 (tests): ADDRESSED. The two-player test (weeks 9 and 10) asserts the full reason with "Josh Jacobs and A.J. Brown return in week 10" and `step == 1`.
   The bench test asserts the full reason "... gains now." and `step == 1`.

New breakage in the fix diff: none found. The change to `adjusters.py` only moves the call into a variable. Only the docstring and two tests changed beyond that.
