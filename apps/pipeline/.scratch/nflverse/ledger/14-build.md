# 14 build: the short name keeps a two-word last name

Status: DONE_WITH_CONCERNS. Branch `nflverse-14`, commit `3cf0bee`. Not pushed. Not merged.

## What changed

- `src/cornerstone/names.py`: a new tuple `NAME_PARTICLES = ("st.", "st", "saint", "van", "vander", "de", "del", "von")`.
  `last_name` returns "<particle> <last>" when the word before the last word is a particle.
  The match ignores case. The result keeps the original case, such as "de Beer".
- The particle rule applies only when the name has three or more words. "Van Jefferson" stays "Jefferson".
- The old gate still applies to the last word: four letters or more, letters only. "Kyle Van Noy" still gives None.
- A chain such as "De La Cruz" or "van den Berg" keeps the last word only, as before. "La" and "den" are not particles.
- The module docstring names the particles. Every old comment stays.
- `.scratch/nflverse/issues/14-...md`: four boxes ticked. Status stays `open`.

## Tests added

`tests/test_names.py`, 6 tests. Two failed before the change (red), all pass after it.

- `test_last_name_keeps_a_particle_before_the_last_word`
- `test_last_name_is_one_word_without_a_particle` (Jacobs, Harrison)
- `test_a_particle_as_a_first_name_is_not_part_of_the_last_name`
- `test_a_short_last_word_after_a_particle_still_has_no_last_name`
- `test_two_st_browns_in_one_trade_both_show_in_full` (calls `adjusters._short_names`; no edit to `adjusters.py`)
- `test_one_st_brown_in_a_trade_shortens_to_st_brown`

## Checks

- `uv run pytest -q`: `1042 passed, 9 deselected in 185.08s (0:03:05)`. That is 1036 old tests plus 6 new.
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` Same as main. The two changed files are clean.

## Callers of `last_name`

1. `adjusters._short_names`: the trend reason. This is the target. It needs no change.
2. `verifier.code_check`, line 261: `in_scope_last` holds the last names of the scope players.
   `reaction_failures` matches each one with `_whole_pattern`, which escapes the text. "St. Brown" matches as a phrase.
3. `verifier.code_check`, line 308: an out-of-scope player fails when the blurb holds his last name as a whole word.
   `whole_word` uses the same escaped pattern, so a two-word name matches as a phrase.
   The skip on `scope_team_words` compares one word, so a two-word name never hits it. That is correct.
- `analysis.py` imports only `NAME_SUFFIXES`. It does not call `last_name`.
- No match breaks. Both verifier checks now look for "St. Brown", not "Brown".

## Changed names in data/2026/week-06/raw/players.json (11879 names)

20 names changed. No other result changed.

- Alex Van Pelt: Pelt -> Van Pelt
- Amon-Ra St. Brown: Brown -> St. Brown
- Andrew Van Ginkel: Ginkel -> Van Ginkel
- Brian St Pierre: Pierre -> St Pierre
- Cole Van Lanen: Lanen -> Van Lanen
- Equanimeous St. Brown: Brown -> St. Brown
- Gerhard de Beer: Beer -> de Beer
- Greg Van Roten: Roten -> Van Roten
- Jacob De Jesus: Jesus -> De Jesus
- Jason Vander Laan: Laan -> Vander Laan
- Joby Saint Fleur: Fleur -> Saint Fleur
- Ka'ena De Cambra: Cambra -> De Cambra
- La'Kendrick Van Zandt: Zandt -> Van Zandt
- Leighton Vander Esch: Esch -> Vander Esch
- Lukas Van Ness: Ness -> Van Ness
- Micah St. Andrew: Andrew -> St. Andrew
- Mitch Van Vooren: Vooren -> Van Vooren
- Ryan Van Demark: Demark -> Van Demark
- Tyree St. Louis: Louis -> St. Louis
- Zach Von Rosenberg: Rosenberg -> Von Rosenberg

## Concerns

1. The verifier is now less strict for these 20 players. A blurb that writes only "Brown" no longer fails the
   out-of-scope check for St. Brown. A reaction sentence with "Brown" alone no longer fails for an in-scope St. Brown.
   "Brown" alone is ambiguous, so this is probably correct. The reviewer must decide.
2. The verifier is stricter for a new form: a blurb with "St. Louis" fails if Tyree St. Louis is out of scope and
   in the league. The old rule had the same risk with "Louis".
3. "Kyle Van Noy" and "Jack Del Rio" still give None, because the last word is short. "Van Noy" could be a valid short
   name, but the ticket did not ask for it.

## Fix round 1

Finding: an in-scope "St. Brown" failed the out-of-scope check for A.J. Brown and Chase Brown.
The regex found "Brown" inside "St. Brown".

- `src/cornerstone/verifier.py`: `code_check` builds `in_scope_last_words`, the last word of each in-scope last name.
  The out-of-scope check skips a last name in that set.
- The worktree had no data change from the reviewer. No data file is in the commit.
- Covering test: `test_in_scope_two_word_last_name_does_not_name_an_out_of_scope_player` in `tests/test_verifier.py`.
  It failed before the fix with the A.J. Brown failure, and it passes after the fix.
- `uv run pytest -q tests/test_verifier.py tests/test_names.py`: `93 passed in 8.21s`.
- `uv run pytest -q`: `1043 passed, 9 deselected in 158.23s (0:02:38)`.
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` Same as main.
- Side effect: "Brown" alone in a blurb no longer fails for an out-of-scope Brown when a St. Brown is in scope.
  The word is ambiguous there, so this matches the rule for a shared last name.
