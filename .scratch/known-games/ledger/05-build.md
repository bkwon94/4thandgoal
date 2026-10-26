# Ticket 05 build: out with no return week

Status: NEEDS_CONTEXT. No commit. The change sits uncommitted in the worktree on `known-games-05`.

## The conflict

The ticket says two things that cannot both hold with the week 6 fixture:

1. A player in `OUT_STATUSES` with no returns row counts as due back at week 14 for lineup value.
2. Every existing rubric test passes unchanged.

The fixture has 26 rostered players who are out with no returns row. Examples: Saquon Barkley (Out, roster 10),
Lamar Jackson (Out, roster 6), Jacory Croskey-Merritt (IR, roster 4). The fixture also has a projections file.
So rule 1 changes the lineup value of these players in many existing trades. Fit steps flip, and real week 6
trades that the tests grade by hand change.

## What I built

- `src/cornerstone/adjusters.py`: a public `due_back_week(snapshot, player_id) -> int | None`. The returns row
  gives the week. An out player with no row gets `RETURN_BY_WEEK`. A week through `stats_through` gives None.
  `lineup_value`, `projection_ahead`, `_due_back_notes` (the fit note), and `_gain_when` read it.
- `_due_back` stays on the returns file only. The trend and the expected gap read it. My first try widened
  `_due_back` itself, and 20 tests failed. The narrow form leaves 12 failures.
- `src/cornerstone_api/cache.py`: `_content_hash` now builds its due-back map from `due_back_week` over the
  rostered players. Before, it read only `snapshot.returns` and never the injury status. So a move into the out
  set did not change the key. Now the key and the grade use one rule.
- Tests: 4 rubric tests in `tests/test_rubric.py` (after `test_a_player_due_back_in_the_trade_week_counts_for_that_week`),
  and 1 cache key test in `tests/test_api.py`.

## TDD evidence

RED, `uv run pytest -q tests/test_rubric.py -k "out_with or questionable_player or a_player_out"`:

```
E       AssertionError: assert Decimal('3.833333333333333333333333333') == 20
FAILED tests/test_rubric.py::test_a_player_out_with_no_return_week_counts_for_his_projection_ahead_from_week_14
FAILED tests/test_rubric.py::test_without_the_projections_a_player_out_with_no_return_week_keeps_his_recent_points
2 failed, 3 passed, 132 deselected
```

The 3 that pass guard today's behavior: a returns row of week 9, a Questionable player, and the injury dock.

RED, `uv run pytest -q tests/test_api.py -k moves_into_the_out_set`:

```
E       AssertionError: assert '56c06dc9...4e8a' != '56c06dc9...4e8a'
FAILED tests/test_api.py::test_the_cache_key_changes_when_a_rostered_player_moves_into_the_out_set
```

GREEN, the same 6 tests: `6 passed, 237 deselected`.

## Full suite

Not clean. `uv run pytest -q tests/test_rubric.py tests/test_api.py` with the narrow form: `12 failed, 231 passed`.
Ruff on the first try was clean. I did not run it again on the narrow form.

The 12 failures, by kind:

- Reason text only: the fit reason gains "Saquon Barkley is due back in week 14, so he counts for his projection
  ahead of 12.6 a game." Tests at lines 162, 177, and 140 (that one bans digits in the breakdown text).
- Step flips: fit -1 where the test wants 1 (lines 185, 343, Lamar Jackson), and 1 where it wants 0 (line 199).
- Real week 6 trades worked by hand: cases 0, 2, and 5 of `test_each_real_week_6_trade_grades_as_worked_by_hand`
  change the fit step at index 0.
- `test_a_player_not_due_back_keeps_his_recent_points_whatever_his_projection`: its premise is that Saquon is not
  due back. Under the ticket's rule he is.
- `test_without_the_projections_every_grade_is_as_by_recent_points_and_the_reason_says_so`: its "today" grade
  sets `returns` to `{}` to make Jacobs not due back. Jacobs is `Sus`, so he is now due back at 14 there too.
- `test_the_find_fixture_reasons_pass_the_real_reason_checks`: the finder picks other trades.

## Decision needed

Pick one:

1. Accept the rule as written. Update the 12 tests to the new grades, and rework the hand-worked week 6 numbers.
   This is the spec's intent ("his value drops the same day Sleeper tags him"). About 1 to 2 hours.
2. Drop the "unchanged" criterion for tests whose fixture players are out with no row, and give those tests a
   returns row or a healthy status so their premise holds. Smaller, but it edits test setup.
3. Narrow the rule further, for example only for players with a projections row at or after week 14. This
   departs from the spec.

## Self-review

- `due_back_week` reads `snapshot.players[player_id]`. The cache now calls it for every rostered player. No API
  test hit a KeyError, so every rostered id is in `players` in the fixtures.
- `_gain_when` uses the widened rule, so a lineup gain from an out player says "after ... in week 14".
  This matches the fit note. The ticket does not say it, so the reviewer should confirm.
- The trend and the expected gap keep the returns-only `_due_back`. The ticket does not ask for a change there.

---

# Follow-up after the controller ruling

The ruling: the spec rule stands. The second form stays: lineup value, the fit note, and the gain time widen.
The trend and the expected gap keep the returns file. The "unchanged" criterion is replaced.

Status: DONE_WITH_CONCERNS. Committed on `known-games-05`.

## More changes

- The fit note for a player with no returns row now reads "X has no return week on file, so he counts as back in
  week 14 for his projection ahead of N a game." A player with a returns row keeps "X is due back in week W, so he
  counts for his projection ahead of N a game." Why: a player with no row has no known return, so "is due back"
  claims too much. The new sentence lives in `_due_back_note` in `src/cornerstone/adjusters.py`.
- The cache key also hashes `on_file`: the due-back players with a returns row. Why: a returns row of week 14 and
  no row both give week 14, but the reason words differ. The cache key test checks this case too.
- `tests/fixtures/api/find-response.json`: trade 1 is the finder's new first trade, with a hand-written reason.

## Rule 1: the tests that pin the new grade

| Test | Old | New | Why the new value follows the rule |
| --- | --- | --- | --- |
| `test_fit_steps_up_for_a_lineup_gain_and_down_for_a_lineup_loss` | both reasons with no note | the same steps, and each reason ends with the Saquon note | Saquon is Out with no row, so the fit note names him in week 14 at 12.6. |
| `test_fit_steps_up_for_the_highest_value_player_in_the_trade_with_no_lineup_loss` | roster 10 fit 0, roster 12 reason with no note | roster 10 fit -1, roster 12 reason ends with the Saquon note | Roster 10 gives his 12.6 for Pollard at 8.95, a loss past the threshold. |
| `test_an_unlisted_player_makes_points_per_game_pick_the_highest_value_player_in_the_trade` | roster 10 fit 1, roster 12 fit 0 | roster 10 fit -1, roster 12 fit 1 | Saquon at 12.6 tops Pollard at 8.95, so roster 12 gets the highest-value player. |
| hand-worked trade 0, roster 7 | fit -1, final F | fit 1, final D | Breece Hall counts at 11.7 from week 14. The lineup does not lose, and roster 7 gets the highest-value player. The verdict stays accept. |
| hand-worked trade 2, roster 6 | fit -1, standing -1, final F | fit 0, standing 0, final F | Lamar counts at 22.7 from week 14. The lineup stays about the same, so no loss now and no standing step. The verdict stays accept. |
| hand-worked trade 5, roster 4 | fit -1, final F | fit 0, final F | Croskey-Merritt at 6.8 and Montgomery at 10.3 count from week 14. The lineup stays about the same. The verdict stays accept. |
| `test_the_find_fixture_reasons_pass_the_real_reason_checks` | trade 1: Tucker and Aaron Jones for Derrick Henry | trade 1: Tucker and Wan'Dale Robinson for Jameis Winston | Out players on rosters 2 and 3 now count for their projections, so the finder ranks other trades first. Trades 2 and 3 do not change. |

The new finder reason: "All You Need Is Love gets Jameis Winston, the best player in the trade, with no loss to
its lineup, and Lil Fridge gets Tre Tucker and Wan'Dale Robinson into its best lineup."

## Rule 2: the tests that keep their grade with a changed setup

- `test_the_breakdown_holds_no_trade_value_sum_ratio_or_chart_name`: its subject is no digit in a reason.
  Croskey-Merritt is now healthy in the setup, so no note with a projection shows.
- `test_a_player_not_due_back_keeps_his_recent_points_whatever_his_projection`: its premise is that Saquon is not
  due back. Saquon is now healthy in the setup.
- `test_without_the_projections_every_grade_is_as_by_recent_points_and_the_reason_says_so`: its "today" grade
  makes Jacobs healthy as well as giving him no row. Its "no player due back" trade makes Saquon healthy.

Two tests have a roster fit subject, but I put them under rule 2. Pinned to the new grade, each one would test
nothing of its own rule:

- `test_the_side_that_gets_the_depth_steps_up_only_when_every_player_it_gets_starts`: the new grade is fit 1, so
  the "not every player it gets starts" branch would lose its only test. Roster 10 holds Monangai and Judkins,
  who are also Out with no row. So the setup drops the projections file and makes Saquon healthy.
- `test_a_lineup_change_below_the_fit_threshold_is_no_loss_for_the_highest_value_player_step`: the new grade is
  fit -1, so the threshold branch would lose its test. Lamar is now healthy in the setup, at 19.66.

## Three new week 6 reasons

1. Trade 0, roster 7 fit: "It gets the highest-value player in the trade, and the best lineup does not lose.
   Breece Hall has no return week on file, so he counts as back in week 14 for his projection ahead of 11.7 a game."
2. Trade 2, roster 7 fit: "The best lineup gains after the trade. Lamar Jackson has no return week on file, so he
   counts as back in week 14 for his projection ahead of 22.7 a game."
3. Trade 5, roster 12 fit: "It gets the highest-value player in the trade, and the best lineup does not lose.
   Jacory Croskey-Merritt has no return week on file, so he counts as back in week 14 for his projection ahead of
   6.8 a game. David Montgomery has no return week on file, so he counts as back in week 14 for his projection
   ahead of 10.3 a game."

## Verification

- `uv run pytest -q`: `1088 passed, 9 deselected in 218.90s`.
- `uv run ruff check src tests`: exit 0, clean.
- The cache key test fails with the change to `cache.py` stashed, and passes with it.

## Concerns

1. `find-response.json` is shared with the site repo. The site copy needs the same trade 1 change.
2. The trade 5 fit reason has two long note sentences. It reads correctly, but it is long. A joined form for two
   or more players is a possible follow-up.
3. The two roster fit tests under rule 2 go against the letter of the ruling. The reason is above.
4. Late in the season, at `stats_through` 14 or later, an out player with no row is no longer due back. He then
   keeps his recent points of about 0. A player with a past returns row does the same today.
5. `DOCUMENT_VERSION` does not bump. The keys of affected rosters change through the content hash, so no stale
   grade serves. The PRD bumps the version in the cache key ticket.

---

# Fix round 1

Status: DONE. One commit with the five review fixes and this report.

## Fixes

1. Important. The lineup numbers in the test comments. I checked every one with a probe that calls `build_side` and
   `lineup_value` on the fixture snapshots. The reviewer's numbers match. The fix also covers lines the review did
   not name:
   - Roster 10: Saquon 12.64 and Judkins 8.94 at RB, Monangai 8.44 and Deebo Samuel 8.32 at flex, Ferguson 8.03 on
     the bench.
   - The Cook trade: a gain of 6.46 and a loss of 6.46. Cook takes Saquon's RB spot, and Saquon takes Cook's.
   - Cook and Hubbard: a gain of 15.41. Deebo Samuel moves to the bench.
   - Roster 12: DJ Moore, Out with no row, holds the last flex spot at 12.20. Hampton 9.70 and Pollard 8.95 sit.
   - The Pollard trade: roster 10 loses 3.69.
   - The McCaffrey trade (not in the review): a loss of 4.99, not 10.45. Saquon at 12.64 takes McCaffrey's spot at
     17.63.
   - HAND_WORKED: trade 0, roster 7 -2.18 and roster 8 0.34. Trade 1 (not in the review): roster 11 -6.94 and
     roster 12 5.57. Trade 2: roster 6 -0.22 and roster 7 4.15. Trade 3 (not in the review): roster 4 4.75 and
     roster 7 -4.63. Trade 4 (not in the review): roster 7 -1.05. Trade 5: roster 4 0.14 and roster 12 -0.59.
   - The fit threshold test: "gains 8.48" is now "gains 4.15". Its week 7 change of -0.60 holds with Lamar healthy.
2. `_due_back` has a comment line: "The trend and the expected gap read only the returns file, so an out player
   with no row keeps his use."
3. `test_a_player_out_with_a_return_week_counts_from_that_week`: week 14 is now 40.0. The mean from week 9 is 20.0.
   The mean from week 14 would be 40.0, so the test can tell the two rules apart.
4. `_gain_when`: when a due-back starter has no returns row, the text is "from week 14, when Saquon Barkley counts
   as back". The returns-row text stays the same. The test came first:
   `test_a_contender_whose_lineup_gain_comes_from_a_player_out_with_no_return_week_says_he_counts_as_back`.
   - RED: `uv run pytest -q tests/test_rubric.py -k "says_he_counts_as_back or a_player_out_with_a_return_week"`
     gave `1 failed, 1 passed`, with
     `+ eup gains after Saquon Barkley returns in week 14.` against `- eup gains from week 14, when Saquon Barkley counts as back.`
   - GREEN: the rubric file gives `138 passed`.
5. HAND_WORKED trade 5: the comment lines are joined. I also rewrapped the trade 0 and trade 2 comments, because
   they went past 120 characters.

## Verification

- `uv run pytest -q tests/test_rubric.py tests/test_api.py`: `244 passed in 94.30s`.
- `uv run pytest -q`: `1089 passed, 9 deselected in 217.71s`.
- `uv run ruff check src tests`: exit 0. The last ruff fix changed only the wrap of a comment, and
  `tests/test_rubric.py` then gave `138 passed`.

## Concern

- With a mix of players in `_gain_when`, some with a returns row and some without, the text uses the "counts as
  back" form for all of them. The fixture has no such case.

---

# Fix round 2

Status: DONE. The branch was at `7b14df8` after the rebase onto main with ticket 01. I did not rebase again.

## Fix

1. `due_back_week` in `src/cornerstone/adjusters.py` now reads `snapshot.as_of.completed_through`, as `_due_back`
   and `_return_bet` do. A return week of N is then still ahead when `stats_through` moves to N.
   - `src/cornerstone_api/cache.py`: my lines read no bound. `_content_hash` reads the bound through
     `due_back_week`, so the key follows the same read. The `stats_through` entries at lines 42 and 102 are not
     mine, and I did not change them.
   - I added no other read of either bound.
2. A test sits beside the return bet bound test:
   `test_the_lineup_value_of_a_player_due_back_reads_the_completed_week_bound_and_not_the_player_stat_bound`.
   With `stats_through` 7 and `completed_through` 5, Jacobs, back in week 7, still has `due_back_week` 7 and a
   `lineup_value` of 18. The fit note still names him as due back in week 7.

## TDD evidence

RED, `uv run pytest -q tests/test_rubric.py -k "lineup_value_of_a_player_due_back_reads"`:

```
E       AssertionError: assert None == 7
1 failed, 140 deselected in 0.28s
```

GREEN, `uv run pytest -q tests/test_rubric.py tests/test_api.py`: `247 passed in 93.66s`.

## Verification

- `uv run pytest -q`: `1097 passed, 9 deselected in 222.37s`.
- `uv run ruff check src tests`: exit 0. The first run flagged the longer `cornerstone.adjusters` import in
  `tests/test_rubric.py`, so the import now sits in parentheses.
