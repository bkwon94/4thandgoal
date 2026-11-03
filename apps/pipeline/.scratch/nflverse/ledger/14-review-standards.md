# 14 review: standards

Verdict: no Critical, no Important. Two Minor notes.

## Critical
clean

## Important
clean

## Minor
1. src/cornerstone/names.py:9 - `NAME_PARTICLES` is a tuple, but `NAME_SUFFIXES` (line 6) is a set. Membership works the same. Fix: use a set literal if "same shape" means the same type.
2. .scratch/nflverse/issues/14-the-short-name-keeps-a-two-word-last-name.md:16-19 - the diff ticks the four boxes. This is outside the code, but it is the normal ledger step. Fix: none, unless the owner wants only code in the diff.

## Checked and fine
- Match is case-insensitive the same way: `.lower()` on the word, lowercase entries.
- Smallest change: `adjusters.py` untouched. The `if` split of the old return is needed for the particle check.
- No old comment removed. The new comments say why. The `_short_names` docstring stays true.
- No "new" or "improved" name. No mock mode.
- Tests assert real values. Test names say what they check. The two `Van` tests guard the first-name and short-word edges.
- STE: comments and docstrings use active voice, present tense, short sentences, no `-ing` verb.
- Extra particles ("saint", "vander", "del", "st") go past the ticket examples, but "such as" allows them.
