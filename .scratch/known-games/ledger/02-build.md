# 02 build: the known-games week

Status: DONE_WITH_CONCERNS. Branch `known-games-02`, base `92b540b`. Not pushed.

## What I built

A grade on a game day of week N now reads the week N games that have a stat line.

- `build_snapshot` parses week N with `parse_past_week(raw, N)` when three things hold:
  1. A trade week is passed, so the raw is a fetch and not a saved week.
  2. The raw week is the trade week (`week.week == trade_week`).
  3. The history holds week N-1 (`completed_through == N-1`).
- When `raw["stats"]` is not empty, week N joins the history for player stats and `stats_through` becomes N.
- `completed_through` stays N-1. The standings get a `History` copy with `week = completed_through`. So `history.complete()` and `season_records` stop at N-1.
- When `raw["stats"]` is empty, `stats_through` stays N-1, the block is None, and `stale` gets `"stats"`.
- A saved week (`load_snapshot`, no trade week) grades exactly as before. The Tuesday roll path (`week.week == through`) does not change.
- The result document and the finder document carry the block as `as_of.known_games`.
- The CLI as-of output has one more line when the block is there: `Known games of week 7: 13 read, 0 in progress.`

## The block shape

```python
class KnownGames(BaseModel):
    week: int                 # the trade week N
    games: int                # distinct week N game_id values with a row whose stats has gp > 0
    in_progress: int = 0      # ticket 04 fills it
    pending: dict[str, int] = {}  # ticket 03 fills it
```

`AsOf.known_games: KnownGames | None = None`. In the documents it is `model_dump()` or `null`.

## Carried items from the ticket 01 review

- Hidden standings read: done. The standings get `history.model_copy(update={"week": completed_through})`. The test `test_the_standings_of_a_known_games_week_count_the_games_of_weeks_1_to_5_only` checks that the standings of a known-games build equal the saved build and count 5 * 2 * 12 games. That test passed before the change too, because `complete()` only checks presence and `season_records` already took `completed_through`. It guards against a later change that passes `stats_through` to the standings.
- The comment "The standings run through the same week as the stats." is replaced.
- Docstrings: `recent_points_per_game`, `_red_zone_touches`, the `Snapshot.week` and `Snapshot.stats` comments, the `trade_facts.py` file docstring, `_ppg_fact`, and `trade_fact_sheet` now name the player stat bound or the known games.
- Bound guards in `tests/test_rubric.py`: two new tests on a real known-games snapshot, where `stats_through` is 6 and `completed_through` is 5.
  - `test_the_return_bet_of_a_known_games_week_reads_the_completed_week_bound`: a return in week 6 is still a return bet. A reader on `stats_through` fails it.
  - `test_the_player_stat_readers_of_a_known_games_week_read_its_games`: McCaffrey's recent points per game is 19.025 with week 6 and 17.625 without it. A reader on `completed_through` fails it.
  - The two older guard tests stay as they were.

## Files changed

- `src/cornerstone/snapshot.py`: `KnownGames`, `AsOf.known_games`, `_games_with_a_stat_line`, the build, the standings bound, comments.
- `src/cornerstone_api/analyzer.py`: `_as_of` adds `known_games`.
- `src/cornerstone/cli.py`: the known-games line under the as-of line.
- `src/cornerstone/adjusters.py`, `src/cornerstone/trade_facts.py`: docstrings only.
- `tests/test_snapshot.py`, `tests/test_rubric.py`: new tests.
- `tests/test_api.py`, `tests/test_live.py`, `tests/test_cli.py`: changed expectations, listed below.
- `tests/fixtures/api/analyze-response.json`, `tests/fixtures/api/find-response.json`: `known_games` in `as_of`.

## Existing tests that changed, and why

The API, live, and CLI tests fetch the week 6 raw on Monday 2026-10-19, with trade week 6. That fetch holds the week 6 stat lines, so it is now a known-games build.

1. `test_a_good_request_returns_the_result_document`: `as_of` is now `stats_through: 6`, `completed_through: 5`, and the block with 14 games.
2. `test_the_cache_key_ignores_the_projection_rows_of_a_player_already_back`: it used `stats_through` as "a past return week". That is a wrong bound read in the test. It now uses `completed_through`.
3. `find_sources` (the finder trade-set tests): the fetch has empty stats, as before the first week 6 game. With week 6 read, the finder finds 1 win-win trade, not 3. The find fixture is shared with the site and holds hand-written reasons for those 3 trades. So the fixture keeps its trades, and the finder tests keep their intent.
4. `test_find_with_no_win_win_gives_the_empty_line_and_makes_no_claude_call`: it now also checks that the finder document has `stats_through: 6`, `completed_through: 5`, and the block. This is the "finder reads the same bound" check.
5. `NUMBER_KEYS` adds `week`, `games`, `in_progress`.
6. `test_on_monday_night_..._stays_out_of_the_history` is renamed `..._its_known_games_stay_out_of_the_saved_history`. It now checks bound 6, standings bound 5, 14 games, standings of weeks 1 to 5, and no saved week 6 folder.
7. `test_a_failed_history_fetch_keeps_the_saved_weeks_and_notes_it`: it adds `known_games is None`.
8. CLI: the as-of test expects `Stats through week 6.` and the known-games line. The failed-refresh test expects no known-games line.

## TDD evidence

RED, snapshot (after the `KnownGames` model existed, before the build):
```
uv run pytest -q tests/test_snapshot.py
E       AssertionError: assert 5 == 6
E       AssertionError: assert [] == ['stats']
FAILED tests/test_snapshot.py::test_a_trade_week_with_stat_lines_reads_its_known_games_and_keeps_the_standings_at_the_week_before
FAILED tests/test_snapshot.py::test_a_trade_week_with_no_stat_lines_keeps_the_bound_at_the_week_before_and_names_the_stats_stale
2 failed, 15 passed in 2.63s
```

RED, rubric:
```
uv run pytest -q tests/test_rubric.py -k "known_game or 30_point or completed_week_bound or player_stat_bound"
E       assert (5, 5) == (6, 5)
E       AssertionError: assert Decimal('17.625') == Decimal('19.025')
E       AssertionError: assert Decimal('17.7') == Decimal('21.8')
E       AssertionError: assert 5 == 6
E       AssertionError: assert 'over weeks 5 and 6' in '... Odunze: snap share 93%, up, target share 25%, up, over weeks 4 and 5. ...'
5 failed, 2 passed, 133 deselected in 1.10s
```

GREEN, snapshot and rubric:
```
uv run pytest -q tests/test_snapshot.py tests/test_rubric.py
157 passed in 12.24s
```

RED, API document:
```
uv run pytest -q tests/test_api.py
E       Right contains 1 more item:
E       {'known_games': {'games': 14, 'in_progress': 0, 'pending': {}, 'week': 6}}
E       KeyError: 'known_games'
FAILED tests/test_api.py::test_a_good_request_returns_the_result_document
FAILED tests/test_api.py::test_find_with_no_win_win_gives_the_empty_line_and_makes_no_claude_call
2 failed, 103 passed in 83.24s
```
After `_as_of`, the two fixture shape tests failed until the fixtures got `known_games`. Then:
```
uv run pytest -q tests/test_api.py -k "fixture_shape or fixture or number_outside"
6 passed, 99 deselected in 7.86s
```

RED, live and CLI (the gap guard and the CLI line):
```
E       AssertionError: assert 6 == 4
E       AssertionError: assert '...Stats through week 6. ...\nKnown games of week 6: 14 read, 0 in progress.\n' in '...'
E       AssertionError: assert 'Stats through week 4.' in '...Stats through week 6. ...'
3 failed, 1 passed, 47 deselected in 1.75s
```
GREEN:
```
10 passed, 58 deselected in 2.08s
```

## Full suite and ruff

```
uv run ruff check src tests
(no output, exit 0)

uv run pytest -q
1099 passed, 9 deselected in 218.81s (0:03:38)
```

## Real-data check

Monday 2026-10-26, about 10:50 ET, before the Monday night game.

```
make analyze A=11:5850 B=3:6806 ASKER=3
Week 7 of 2026. Chart week 7. Stats through week 7. Rosters fetched 2026-10-26T10:49-04:00.
Known games of week 7: 13 read, 0 in progress.
Sources: schedules, depth charts, points allowed, injuries, expected points, player weeks.
```

The Monday night game has rows with no `gp` yet, so it does not count. The raw holds 13 game ids, all with a played line.

That trade has no reason that quotes a week 7 number. Sleeper has not posted the Sunday snaps (`off_snp` is null for 292 of 338 played lines), so the Dobbins snap share skips week 7 and reads "over weeks 5 and 6". No week 7 zero is read. This is the pending case of ticket 03.

A second run quotes week 7:
```
make analyze A=11:5859 B=3:9488 ASKER=3
  Trend and usage: one step up. The players it gets gain snap or target share, and the players it gives lose it. Jaxon Smith-Njigba: target share 38%, up, over weeks 6 and 7.
```
Smith-Njigba had 12 targets in week 7.

## Self-review

- Each changed code file keeps its two-line opening docstring.
- No reason, stamp, or docstring says "live", "partial", or "current week".
- `_due_back`, `due_back_week`, and `lineup_value` have no code change. `cache.py` has no change. The key already hashes `stats_through`.
- `recent_points_per_game` keeps a calendar window of `LINEUP_WEEKS` weeks that ends at `stats_through`. A player with no week N line skips week N, as for a bye. He never gets a zero game.

## Concerns

1. Empty week N stats name `"stats"` as stale, as the brief says. Sleeper returns `[]` for a week with no game yet (checked: `/stats/nfl/2026/8` gives `[]`). Sleeper flips `display_week` to N some time before the Thursday game. So from that flip to the Thursday kickoff, every grade says stats are stale, but nothing failed. The ticket also says the new trade week has "zero games read". A fix is a block with 0 games and no stale entry, but then a real outage looks the same. The controller must choose.
2. The gap guard is mine: week N joins only when the history holds week N-1. Without it, a failed history fetch gave "Stats through week 6" with week 5 missing, and most stat readers return None on a gap. The brief does not cover this case.
3. The game count reads only rows with `gp > 0`. Sleeper posts rows with only `gms_active` before a kickoff. With every row counted, today's count would be 14 and would include the Monday night game.
4. The recent points window slides to N-3..N for every player. A player whose week N game is later loses his week N-4 game from the window until he plays. Ticket criterion 4 says he "keeps the points per game of weeks 1 to 6". The season points per game fact does keep it, and the test checks that. The 4-week lineup window does not. A per-player window end is a judgment call. I did not build it.
5. The returns file has Jacobs back in week 7, and his week 7 line has 17.6 points. The due-back rule still gives him his projection ahead, because the rule reads `completed_through` (6). Ticket 05 owns that rule.
6. The cache key keys on `stats_through` only. During week N a repeat grade can serve old numbers until ticket 06 hashes the stat lines.
7. The find fixture keeps `stats_through: 5` and `known_games: null`, and the analyze fixture has `stats_through: 6` with a 14-game block. The site repo copy of both fixtures needs the same field (ticket 08).

## Fix round 1

This round follows the review rulings. Build concerns 1 and 4 are closed.

What I changed:
1. The gate. Week N joins the player stats only when the count of games with a played line (`gp > 0`) is above 0. With only `gms_active` lines, `stats_through` stays N-1 and the block is `KnownGames(week=N, games=0)`.
2. The window. `recent_points_per_game` ends at N for a player with a week N line where `gp > 0`, and at `completed_through` for every other player. So a player's points per game move only when he plays. The test now uses McCaffrey, who played every week from 1 to 5. With his week 6 line removed, his value is 17.625 on both snapshots.
3. Failed or empty. `fetch_live_raw` fetches the stats with a new `_get_or_none`, so a failed call gives `stats: None` and a good empty call gives `[]`. `fetch_past_week` and `_get_or_empty` do not change.
   - `build_snapshot` reads `raw.get("stats")`. It passes a raw with `[]` to the parses, so a missing key or None raises no error.
   - `parse_week` reads `raw.get("stats") or []`, because `fetch_current_week` parses the live raw before the snapshot.
   - None or a missing key: the block is None and `"stats"` is stale.
   - `[]`: the block has 0 games and nothing is stale.
   - The find fixture now has the 0-game block.
4. The `build_snapshot` docstring states the contract: a saved week passes no trade week and never counts its own games. Only the live path passes one.
5. `test_the_player_stat_readers_of_a_known_games_week_read_its_games` now also checks for "over weeks 5 and 6" in the trend reason. It also checks for "Every stat runs through week 6." in the `trade.week` fact.
6. `from decimal import Decimal` is now in the stdlib group.

The Tuesday roll does not change. The block is None then.

Files: `src/cornerstone/snapshot.py`, `src/cornerstone/sleeper.py`, `src/cornerstone/parse.py`, `src/cornerstone/adjusters.py`, `tests/test_snapshot.py`, `tests/test_rubric.py`, `tests/test_sleeper.py`, `tests/fixtures/api/find-response.json`.

RED:
```
uv run pytest -q tests/test_snapshot.py tests/test_rubric.py tests/test_sleeper.py
E       AssertionError: assert None == KnownGames(week=6, games=0, in_progress=0, pending={})
E       AssertionError: assert 6 == 5
E       TypeError: 'NoneType' object is not iterable
E       AssertionError: assert Decimal('16.63333333333333333333333333') == Decimal('17.625')
E       assert [] is None
FAILED tests/test_snapshot.py::test_a_trade_week_with_no_stat_lines_keeps_the_bound_at_the_week_before_and_reads_zero_games
FAILED tests/test_snapshot.py::test_a_trade_week_with_only_lines_of_active_players_keeps_the_bound_at_the_week_before
FAILED tests/test_snapshot.py::test_a_failed_stats_fetch_keeps_the_bound_at_the_week_before_and_names_the_stats_stale
FAILED tests/test_rubric.py::test_a_player_with_no_known_game_keeps_his_points_per_game_and_no_zero_game
FAILED tests/test_sleeper.py::test_a_failed_live_stats_fetch_gives_no_stats_and_a_good_empty_one_gives_an_empty_list
5 failed, 166 passed, 3 deselected in 12.25s
```
The item 5 checks passed before the fix. They guard a share reader against the wrong bound.

GREEN:
```
uv run pytest -q tests/test_snapshot.py tests/test_rubric.py tests/test_sleeper.py
171 passed, 3 deselected in 12.47s
uv run pytest -q tests/test_live.py tests/test_api.py tests/test_cli.py
156 passed in 93.95s (0:01:33)
uv run ruff check src tests
RUFF_OK (no findings)
uv run pytest -q
1102 passed, 9 deselected in 223.82s (0:03:43)
```

Real-data recheck, 2026-10-26 11:10 ET:
```
make analyze A=11:5859 B=3:9488 ASKER=3
Week 7 of 2026. Chart week 7. Stats through week 7. Rosters fetched 2026-10-26T11:10-04:00.
Known games of week 7: 13 read, 0 in progress.
  Trend and usage: one step up. ... Jaxon Smith-Njigba: target share 38%, up, over weeks 6 and 7.
```

Open concerns: 5, 6, and 7 from the build stand. These are the Jacobs due-back rule (ticket 05), the cache key (ticket 06), and the site fixture copy (ticket 08).
