# 01 build: two bounds in the stamp

Status: DONE_WITH_CONCERNS. Commit `0dda83d` on `known-games-01`, base `3656433`. Not pushed. This report is not committed.

## What I built

`AsOf` now has two bounds. Both hold the same week as the one field held before, so no grade changes.

- `stats_through`: the player stat bound. Every player stat reader takes it as its `through`.
- `standings_through`: the standings bound. The standings build, the return bet (`back_inside`), the due-back rule, and the injury report week count read it.

`build_snapshot` sets `standings_through = stats_through`. Ticket 02 changes only the player bound.
The result document and the finder document (`_as_of`) carry both. `stats_through` keeps its value, so the site reads as before.

## Why these names

- `stats_through` stays the player bound. The stat readers already take a `through` argument. The site reads `stats_through` as "Stats through week N". In ticket 02 that label stays true. The cache key keeps the same field, so every key keeps its value.
- `standings_through` matches the ticket and PRD term "standings bound". The glossary entry "Before the trade" says "The standings and the chart week end there". A name such as `completed_through` covers the return weeks and the injury reports better. But it does not match the glossary or the tickets, so I chose `standings_through`.

## Which reader takes which bound

Player stat bound, `stats_through`, no edit needed:
- `recent_points_per_game`, `_wopr`, `_directions`, `_share_sentences`, `_red_zone_touches` in `adjusters.py`.
- The ppg, share, and red zone facts and `_week_fact` in `trade_facts.py`.
- `History(week=...)` in `snapshot.py`, the CLI as-of line, and the cache key fields in `cache.py`.

Standings bound, `standings_through`, changed:
- `standings(...)` in `build_snapshot`.
- `_return_bet` (`back_inside`) and `_due_back` in `adjusters.py`.
- `_report_weeks` in `adjusters.py` and `trade_facts.py`.
- The `due_back` filter in `_content_hash` in `cache.py`.

## Files changed

- `src/cornerstone/snapshot.py`: the two fields with comments, the build, and the "Before the trade" comment.
- `src/cornerstone/adjusters.py`: `_return_bet`, `_due_back`, `_report_weeks`, and the "Before the trade" comment.
- `src/cornerstone/trade_facts.py`: `_report_weeks`.
- `src/cornerstone_api/analyzer.py`: `_as_of` adds `standings_through`.
- `src/cornerstone_api/cache.py`: the `due_back` filter.
- `tests/test_snapshot.py`, `tests/test_api.py`, `tests/test_rubric.py`: the tests below.
- `tests/fixtures/api/analyze-response.json`, `tests/fixtures/api/find-response.json`: `standings_through: 5` in `as_of`.

## TDD evidence

RED. These tests come first:
- `test_week_6_snapshot_is_the_trade_week_and_its_inputs_end_at_week_5` checks `standings_through == 5`.
- `test_a_history_without_week_5_stamps_the_last_week_it_holds_and_notes_it` checks `standings_through == 4`.
- `test_a_good_request_returns_the_result_document` checks the full `as_of` with both bounds.
- `test_find_returns_three_win_win_trades_with_one_reason_each` checks both bounds in the finder `as_of`.
- `test_the_return_bet_reads_the_standings_bound_and_not_the_player_stat_bound` is a new test.
- `test_the_player_stat_readers_read_the_player_stat_bound_and_not_the_standings_bound` is a new test.

```
uv run pytest -q tests/test_snapshot.py tests/test_api.py tests/test_rubric.py -k "standings_bound or player_stat_bound or week_5 or inputs_end or returns_the_result_document or win_win_trades_with_one_reason"
E                   AttributeError: 'AsOf' object has no attribute 'standings_through'
E                   AttributeError: 'AsOf' object has no attribute 'standings_through'
E         Right contains 1 more item:
E         {'standings_through': 5}
E       KeyError: 'standings_through'
E       AssertionError: assert 0 == 1
E        +  where 0 = Adjuster(name='standing', step=0, reason='The team holds a playoff spot, and the trade is no win-now move or return bet.', lean=None).step
FAILED tests/test_snapshot.py::test_week_6_snapshot_is_the_trade_week_and_its_inputs_end_at_week_5
FAILED tests/test_snapshot.py::test_a_history_without_week_5_stamps_the_last_week_it_holds_and_notes_it
FAILED tests/test_api.py::test_a_good_request_returns_the_result_document - A...
FAILED tests/test_api.py::test_find_returns_three_win_win_trades_with_one_reason_each
FAILED tests/test_rubric.py::test_the_return_bet_reads_the_standings_bound_and_not_the_player_stat_bound
5 failed, 1 passed, 247 deselected in 4.98s
```

The player stat reader test passed on the old code. That is expected. The old `model_copy` puts an unknown field on the stamp, and no reader reads it. The test guards ticket 02 against a reader that takes the wrong bound.

The first full run after the change had 3 failed tests. They pin the document shape: `test_the_document_has_no_number_outside_ids_weeks_and_the_stamp` and the two fixture shape tests. I added `standings_through` to `NUMBER_KEYS` and to the two API fixtures. Without the fixture edit, `test_a_good_request_returns_the_document_in_the_fixture_shape` fails.

GREEN:
```
uv run pytest -q
1085 passed, 9 deselected in 222.88s (0:03:42)
```

Ruff:
```
uv run ruff check src tests
exit=0
```

## Self-review

- No grade changes. Both bounds have the same value, and the cache key fields are the same, so every stored key still hits.
- The two "Before the trade" comments now match the glossary. The standings end at N-1, and player stats end at the known games.
- I kept the comment "The standings run through the same week as the stats." It is true now. Ticket 02 makes it false, so ticket 02 must change it.
- Each file keeps its two-line opening docstring.

## Concerns

1. The ticket says "every existing test passes unchanged". The ticket also says the document carries both bounds. These two conflict for 4 existing tests: the exact `as_of` equality, `NUMBER_KEYS`, and the two fixture shape tests. I changed those 4 by one field each. No other existing test changed.
2. `_due_back` and `_report_weeks` read the standings bound. The ticket names only the standings and the standing adjuster for it. I chose the standings bound for these because they count calendar weeks from hand-kept or nflverse files, not Sleeper stat lines. Ticket 02 does not list them as readers that move to week N. `_due_back` also feeds `lineup_value` and must match the `due_back` filter of the cache key, so the two read the same bound. The controller must confirm this choice before ticket 02.
3. The site repo has its own copy of the API fixtures, probably. Ticket 08 can add `standings_through` there. The site does not need it for this ticket.

## Fix round 1

Rulings: concern 1 accepted, concern 3 left for ticket 02. Concern 2: rename the fixed bound.

What I changed:
- `standings_through` is now `completed_through`, the last completed week before the trade week. The rename covers `AsOf`, `build_snapshot`, `_return_bet`, `_due_back`, `_report_weeks` in `adjusters.py` and `trade_facts.py`, the cache `due_back` filter, `_as_of`, the tests, and the two API fixtures.
- The `AsOf` field comment now reads: "The last completed week before the trade week. The standings, the due-back rule, and the injury report end here."
- The `_report_weeks` comment in `adjusters.py` now reads: "GLOSSARY.md, "Before the trade": the injury report ends at N-1, the last completed week."
- The two new rubric tests now say "completed week bound" in their names.
- `GLOSSARY.md`, "Before the trade": "The standings, the chart week, the due-back rule, and the injury report end there. Player stats end at the known games."
- `stats_through` stays the player stat bound.

The sections above use the old name `standings_through`. Read it as `completed_through`.

Check: `grep -rn "standings_through\|standings bound" src tests GLOSSARY.md` finds no match.

Full suite:
```
uv run pytest -q
1085 passed, 9 deselected in 214.58s (0:03:34)
```

Ruff:
```
uv run ruff check src tests
ruff exit=0
```
