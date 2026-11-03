# 14 review: spec compliance and real-data check

Verdict: one Important regression in the name gate. The ticket boxes are met.

Commit `3cf0bee` on `nflverse-14`, base `e29e2b4`.

## Critical

None.

## Important

1. `src/cornerstone/verifier.py:311`: an in-scope "St. Brown" now fails the out-of-scope check for other Browns.
   - Before the change, `in_scope_last` held "Brown", so the skip kept "A.J. Brown" and "Chase Brown" quiet.
   - Now `in_scope_last` holds "St. Brown". The out-of-scope "Brown" matches as a whole word inside "St. Brown".
   - Real-data probe: week 6 `recap_3` has Amon-Ra St. Brown in scope. Both other Browns are in the league.
     I added "St. Brown also played." to sentence 0. Before: no new failure. After:
     `'[0] player A.J. Brown is not on a team in this chapter', '[0] player Chase Brown is not on a team in this chapter'`.
   - This is a false failure on the exact short name that the ticket asks the trend reason to use.
   - Fix: skip an out-of-scope last name when it is the last word of an in-scope last name, for example
     `last in {n.split()[-1] for n in in_scope_last if n}`. Add a test with St. Brown in scope and A.J. Brown out of scope.

## Minor

1. `src/cornerstone/verifier.py:173`: a reaction sentence with "Brown" alone no longer fails for an in-scope St. Brown.
   - "Brown" alone is ambiguous, so this looser rule is acceptable. No fix needed. Record it as known.
2. `src/cornerstone/verifier.py:308`: a blurb with "Brown" alone no longer fails for an out-of-scope St. Brown.
   - In this league, A.J. Brown and Chase Brown still catch "Brown" when they are out of scope.
   - This is correct behavior, not a regression. No fix needed.

## Checklist boxes

1. "Amon-Ra St. Brown" shortens to "St. Brown": met. `tests/test_names.py` `test_last_name_keeps_a_particle_before_the_last_word` and `test_one_st_brown_in_a_trade_shortens_to_st_brown`.
2. Two St. Browns in one trade show in full: met. `test_two_st_browns_in_one_trade_both_show_in_full`.
3. "Josh Jacobs" gives "Jacobs", "Marvin Harrison Jr." gives "Harrison": met. `test_last_name_is_one_word_without_a_particle`.
4. Existing tests pass unchanged: met. `tests/test_verifier.py`, `test_analysis.py`, `test_trades.py`: `179 passed`. `tests/test_names.py`: `6 passed`. The builder reports `1042 passed` for the full suite.
5. `_short_names` in `src/cornerstone/adjusters.py` has no change, as the ticket says.

## Real-data result

- I ran `code_check` over every saved week 6 blurb in `data/2026/week-06/blurbs.json` with the saved facts.
- I ran it with the base `names.py` and with the branch `names.py`.
- The output is identical. 13 chapters pass. `recap_2` fails on both runs with the same old failure:
  `"[0] every sentence has a number (sentences 0, 1, 2); write at least one sentence with no number"`.
- No saved blurb names St. Brown, so the saved data does not show the regression. Only the probe above shows it.

## The 20 changed names

All 20 are sensible short names. None is worse than before.
"Van Ness", "Vander Esch", "Van Ginkel", "St. Brown", "De Jesus", and "Saint Fleur" are the names that broadcasts use.
"St. Louis" and "St. Andrew" are correct surnames. A city match was possible before with "Louis" too.

## Missing from the diff

Nothing that the ticket asks for. The ticket status stays `open`, which is correct before the merge.

## Re-review of fix round 1 (`34fb301`)

Verdict: ADDRESSED.

- `src/cornerstone/verifier.py:263` builds `in_scope_last_words`. The skip at `verifier.py:313` uses it.
- Probe rerun: I added "St. Brown also played." to sentence 0 of week 6 `recap_3`. The branch gives no new failure.
- Full real-data run: the `code_check` output over all saved week 6 blurbs is identical to the base `e29e2b4` output.
  Only `recap_2` fails, with the same old failure about "every sentence has a number".
- `tests/test_verifier.py` and `tests/test_names.py`: `93 passed`.
- Side effect: a bare "Brown" passes for an out-of-scope Brown when St. Brown is in scope.
  This matches the rule for a shared last name, "A last name shared with an in-scope player is ambiguous, so it passes".
  It is also the same as the base: before ticket 14, `in_scope_last` held "Brown" and the skip was the same.
- New breakage: none. For a one-word last name, the set has the same names as `in_scope_last`, so nothing changes.
  Only a last name with a particle adds a word to the set.
- Minor, `tests/test_verifier.py:887`: the test checks A.J. Brown only. Optional fix: also check that no failure names any "Brown".
