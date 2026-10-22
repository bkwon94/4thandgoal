# 08: A team-name word that is also a player's last name fails the code check

**What to build:** The code check removes scope team names before it looks for out-of-scope player names. A pun that reuses one word of a team name, such as "Love is apparently not enough" for All You Need Is Love, leaves the bare word "Love" in the text. The check then matches the last name of Jordan Love and Jeremiyah Love and fails the sentence. The writer retries and the chapter costs a second call, or falls back. We saw it twice in the rankings chapter for week 6.

Fix: when a last name equals a word inside a scope team name, do not count it as a player match in that chapter. Keep the match for a last name that is not part of any scope team name. Add the case to the glossary note on the last-name match.

**Blocked by:** None.

**Status:** done

- [x] "Love is apparently not enough." passes in a chapter whose scope has All You Need Is Love and no player named Love.
- [x] "Hurts had 3 touchdowns." still fails in a chapter whose scope has no Jalen Hurts.
- [x] The glossary note on the last-name match names this case.
- [x] `make test` passes. Ruff stays at 123 or lower.

## Comments

2026-10-22: found in the rankings chapter runs. Attempt 1 failed with `player Jeremiyah Love is not on a team in this chapter` and `player Jordan Love is not on a team in this chapter` on "Love is apparently not enough at 97.48 a week lately."
2026-10-22: built on branch `tone-08`. `code_check` in `src/cornerstone/verifier.py` now skips the last-name match when the last name is a word of a scope team name. The full-name match still fails. Three tests in `tests/test_verifier.py` cover the pun, the full name, and "Hurts". The Reaction sentence entry in `GLOSSARY.md` names the case. `make test`: 681 passed. `make lint`: 123.
