# Ticket 09 build: a known game ends due back

Status: DONE_WITH_CONCERNS. Branch `known-games-09`, base `0c9940b`. Not pushed.

## What I built

All of the rule sits in `src/cornerstone/adjusters.py`.

- `_has_known_game(snapshot, pid)`: true when `stats_through` is past `completed_through` and the week
  `stats_through` line of the player has `gp > 0`. `recent_points_per_game` now reads it too, so the two
  share one test for a known game.
- `_back_in_a_known_game(snapshot, pid)`: true when the player has a returns row of week `stats_through` or
  earlier and a known game. A player out with no row never counts, because that is the player hurt in his game.
- `due_back_week` returns None for a player back in a known game. So the lineup value, the fit note, the gain
  text, and the cache key all read his recent points per game, which count the week N game.
- `_due_back` and `_return_bet` end for the same player. `_credited_return_bets` reads `_return_bet`, so the
  standing step and the injury exemption follow.
- A returns row later than N keeps its week. A player out with no row keeps `RETURN_BY_WEEK`. A player with no
  week N game keeps the rule of ticket 05.

The finder needs no code change. `_out_with_no_return` reads only "out tag and no returns row". A known game
ends due back only for a player with a row, so the finder rule is already in step with `due_back_week`.

The cache needs no code change. `_content_hash` reads `due_back_week`, so his first game drops him from the
`returns` map and drops his projection rows from the key.

## Files changed

- `src/cornerstone/adjusters.py`: the two helpers, `due_back_week`, `_due_back`, `_return_bet`,
  `recent_points_per_game`.
- `tests/test_rubric.py`: 5 tests and 2 helpers after the return bet bound test, and `_return_bet` in the import.
- `tests/test_api.py`: 1 cache key test.
- `tests/test_finder.py`: 1 finder guard test.

## The tests

The case is the known-games snapshot, bounds 6 and 5. Jacobs (NA) gets a returns row of week 6 and a week 6
line. The test helper sets his roster points too, because the points reader reads the roster points first.

1. `test_a_player_due_back_in_the_trade_week_who_played_counts_for_his_recent_points_with_no_return_note`:
   `due_back_week` is None, the lineup value is 21 (his week 6 game), and no fit reason names him.
2. `test_a_player_due_back_in_the_trade_week_with_no_game_yet_counts_for_his_projection_ahead`: guard.
   No game yet gives week 6 and a lineup value of 18.
3. `test_a_known_game_keeps_a_later_return_week_and_the_rule_for_an_out_player_with_no_row`: guard.
   A row of week 7 stays 7. No row stays 14.
4. `test_a_known_game_ends_the_trend_exemption_of_a_player_due_back_in_the_trade_week`: the trend reason has
   "Josh Jacobs is due back, so his use does not count." before his game and no such note after it.
5. `test_a_known_game_ends_the_return_bet_of_a_player_due_back_in_the_trade_week`: `_return_bet` is false, and
   the standing reason of roster 3 does not name him.
6. `test_the_cache_key_reads_a_first_known_game_after_a_return_through_the_due_back_rule` in `tests/test_api.py`:
   his first week N line changes both keys. After it, a change to his week N projection row keeps the hit.
7. `test_an_out_player_back_in_a_known_game_is_a_candidate_and_one_with_no_return_week_is_not` in
   `tests/test_finder.py`: guard. With a row of week 6 and a game he is a candidate. With no row he is not.

## TDD evidence

RED, with the source change stashed:

```
uv run pytest -q tests/test_rubric.py -k "trade_week or known_game_keeps"
E       AssertionError: assert 6 is None
E        +  where 6 = due_back_week(Snapshot(...), '5850')
E       AssertionError: assert 'due back' not in 'The players...s not count.'
E           Jacobs is due back, so his use does not count.
E       AssertionError: assert not True
E        +  where True = _return_bet(Snapshot(...), '5850')
FAILED tests/test_rubric.py::test_a_player_due_back_in_the_trade_week_who_played_counts_for_his_recent_points_with_no_return_note
FAILED tests/test_rubric.py::test_a_known_game_ends_the_trend_exemption_of_a_player_due_back_in_the_trade_week
FAILED tests/test_rubric.py::test_a_known_game_ends_the_return_bet_of_a_player_due_back_in_the_trade_week

uv run pytest -q tests/test_api.py -k "first_known_game_after_a_return"
E       AssertionError: assert ('30c28c12416...5357cd715abe') == ('71711f72c61...c23b18d09838')
1 failed, 116 deselected
```

The cache RED is the last assertion: before the fix his projection row still reached the key after his game.
The finder test passes with and without the change, as a guard.

GREEN: `uv run pytest -q tests/test_rubric.py tests/test_finder.py tests/test_api.py` gives `300 passed`.

## Verification

- `uv run pytest -q`: `1153 passed, 9 deselected in 223.18s`.
- `uv run ruff check src tests`: exit 0, clean.

## Concerns

1. The trend test cannot show a share sentence for Jacobs. He has no game in weeks 3 to 5, so one game gives a
   share with no direction. The test checks the note is gone and that `snap_share` reads week 6 for him.
2. The fixture has no injury report in `known_snap`, so no test shows the injury exemption end on its own. It
   reads `_credited_return_bets`, which reads `_return_bet`, and test 5 covers `_return_bet`.
3. A player with a returns row of week N and a game in progress counts as back. His recent points then read a
   game not yet final. This matches how the points reader treats a game in progress.
4. The real case had a returns row of week 7 and a week 7 game. The fixture week is 6, so the tests use week 6.
