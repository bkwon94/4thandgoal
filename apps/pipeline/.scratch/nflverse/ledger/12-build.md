# Ticket 12 build: the standing reason names the player due back

Status: DONE_WITH_CONCERNS
Branch: `nflverse-12`. Worktree: `/Users/brian.kwon/repos/cornerstone-fantasy-sleeper-weekly-report.nflverse-12`.
Commit: `f95732f` nflverse: the standing reason names the player due back.

## What changed

- `src/cornerstone/adjusters.py`: a new helper `_gain_when(snapshot, side)` returns "now" or "after X returns in week N".
  It names each player due back that the side gets and that starts after the trade (`side.starters_after`).
  It uses `_due_back` and `snapshot.returns`, the same source as the roster fit note.
  With more than one such player, it joins the names with `named(..., 'returns', 'return')` and gives the latest week.
- `_standing`: the contender branch for a lineup gain now reads `f"{lead}, and the best lineup gains {_gain_when(...)}."`.
- `tests/test_rubric.py`: one test added.
- `.scratch/nflverse/issues/12-...md`: three boxes ticked. Status stays `open`.

## Tests

- Added `test_a_contender_whose_lineup_gain_comes_from_a_player_due_back_names_him_and_his_return_week`.
  Roster 3 gets Jacobs for Wicks, Jacobs is due back in week 9 with a projection of 18.0. It failed first on "gains now.".
- The healthy case is the existing `test_a_contender_steps_up_for_a_lineup_gain_now`. It passes unchanged.
- `uv run pytest -q`: `1037 passed, 9 deselected in 183.47s (0:03:03)`. After a line wrap for ruff, `tests/test_rubric.py`: `127 passed`.

## Ruff

`uv run ruff check --line-length 120 src tests`: `Found 135 errors.` Same as main. None added.

## Real-data check

`make analyze A=11:5850 B=3:6806 ASKER=3`, Lil Fridge (roster 3, asked):

    Standing: one step up. The team holds a playoff spot, and Josh Jacobs is due back before the playoffs.

## Concerns

1. The live case does not reach the new branch. Jacobs projects 12.2 a game, and the lineup of Lil Fridge "stays about the same".
   So the standing step comes from the return bet branch, not the lineup gain branch. Only the unit test covers the new text.
2. Without the projections file, a due-back player in the starters still gets "after X returns". His value then is recent points.
   This is a rare case: a player with 0 recent points seldom starts. I kept the rule simple.
3. The seller branch still says "for a lineup gain now". The ticket does not cover it, so I did not change it.

## Fix pass

Commit: see `git log -1` on `nflverse-12` (message "nflverse: cover two players due back and the bench case in the standing reason").

1. `_gain_when`: the result of `named` goes into the variable `returns` first. The f-string has no single quotes now.
2. `_gain_when` docstring: rewritten in STE. It says the text names each starter due back and gives the latest return week of them.
3. Two tests added in `tests/test_rubric.py`:
   - `test_a_contender_whose_lineup_gain_comes_from_two_players_due_back_names_both_and_the_latest_week`:
     roster 3 gives Wicks and Shakir for Jacobs (week 9) and A.J. Brown (week 10). Both start.
     The reason reads "... gains after Josh Jacobs and A.J. Brown return in week 10."
   - `test_a_contender_whose_player_due_back_sits_on_the_bench_gains_now`:
     roster 3 gives Wicks and Shakir for Jacobs and Jonathan Taylor. Jacobs projects 1.0 and sits on the bench.
     The reason reads "... gains now."
   Both tests cover the code as built, so they pass at once. A mutation check proved they can fail:
   with `min` in place of `max` and no `starters_after` filter, both tests failed. I then restored the code.

Commands and last lines:
- `uv run pytest -q tests/test_rubric.py`: `129 passed in 6.37s`
- `uv run pytest -q`: `1039 passed, 9 deselected in 158.50s (0:02:38)`
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` Same as main.
