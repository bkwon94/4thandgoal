# 03 build: pending counts

Status: DONE_WITH_CONCERNS. Branch `known-games-03`, base `67f1a4d`. Not pushed.

## What I built

1. **Pending for snaps.** A known game is pending for snaps when no played line (`gp > 0`) of the game has `tm_off_snp`.
   - `snap_share` needs no code change. `_usage_share` already reads only weeks where the denominator is above 0, so a line with no `tm_off_snp` is skipped and never reads as zero snaps.
   - `target_share`, the points, and `red_zone` read the line, as before.
2. **The WOPR window.** `_read_wopr` in `slow_sources.py` now reads weeks 1 to `through + 1` (the trade week). When the file has no row for the trade week, it reads weeks 1 to `through`, as before. It is still None when the file has no row for `through`.
   - `_wopr` in `adjusters.py` drops a scored week past `completed_through` that has no WOPR row for the player. The window then ends at N-1 and is not None.
3. **The pending dict.** `_pending(stats, week, wopr)` in `snapshot.py` fills `KnownGames.pending` in `build_snapshot`. It counts games, and leaves out a count of 0.
   - `"snaps"`: games with no line that has `tm_off_snp`.
   - `"usage"`: games where no played player has a week N WOPR row. The key is "usage" and not "WOPR", per the controller correction: the page bans the word WOPR.
   - A missing player file (`slow.wopr is None`) is a missing source (`player_weeks` in `missing`), not a pending count.
4. **The trend reason.** No code change. `_share_sentences` already gives the weeks after each percent when the two shares read different weeks. A new test pins it: "Nabers: snap share N% (weeks 4 and 5), up, target share N% (weeks 5 and 6), up."

## Why the snap rule reads `tm_off_snp` at the game level

The brief says a line with no `off_snp` or no `tm_off_snp` is pending. The fixture data shows that rule is wrong for `off_snp`. In the final week 6 data, 32 played lines have `tm_off_snp` but no `off_snp` (15 RB, 11 WR, 4 TE, 2 QB). Sleeper leaves out a 0, so those players had 0 offense snaps, and that is a real zero. 28 DEF lines and 2 others have no snap field at all. A line-level rule makes every final game pending. Sleeper posts the snaps of a game together, so the game-level rule on `tm_off_snp` is the safe test. A final week reads `pending == {}`.

## Files changed

- `src/cornerstone/snapshot.py`: `_pending`, the `KnownGames.pending` comment, the block fill.
- `src/cornerstone/slow_sources.py`: `_read_wopr` reads the trade week when present; the `load_slow_sources` docstring.
- `src/cornerstone/adjusters.py`: `_wopr` window and docstring.
- `tests/test_snapshot.py`, `tests/test_rubric.py`, `tests/test_slow_sources.py`: new and changed tests.
- `tests/test_api.py`, `tests/test_live.py`, `tests/fixtures/api/analyze-response.json`: changed expectations.

## Existing tests that changed, and why

1. `test_load_slow_sources_gives_the_wopr_...` is renamed `..._through_the_trade_week_when_it_has_it`. The fixture player file has week 6, so Golden now has `6: 85`.
2. `test_the_refresh_downloads_a_missing_weekly_player_file_...` (live): it asserted every WOPR week is below the trade week. It now asserts `<=` and that the trade week is there.
3. API: the Monday fetch of week 6 now stamps `pending: {"usage": 8}`. The fixture player file holds week 6 rows of 7 teams in 6 games, so 8 of 14 games lack usage. `test_a_good_request_returns_the_result_document`, the finder test, and `analyze-response.json` carry it. `NUMBER_KEYS` adds `snaps` and `usage`.

## TDD evidence

RED (after the tests, before the code):
```
uv run pytest -q tests/test_snapshot.py tests/test_slow_sources.py tests/test_rubric.py
E       AssertionError: assert KnownGames(we...0, pending={}) == KnownGames(we...={'snaps': 2})
E       AssertionError: assert {} == {'usage': 13}
E         Right contains 1 more item:
E         {6: 85}
E       AssertionError: assert {} == {'snaps': 1}
E       AttributeError: 'NoneType' object has no attribute 'weeks_used'
FAILED tests/test_snapshot.py::test_a_known_game_with_no_snap_count_is_pending_for_snaps
FAILED tests/test_snapshot.py::test_a_player_file_with_no_row_of_the_trade_week_names_usage_pending_for_each_game_it_lacks
FAILED tests/test_slow_sources.py::test_load_slow_sources_gives_the_wopr_of_the_weekly_player_file_through_the_trade_week_when_it_has_it
FAILED tests/test_rubric.py::test_a_known_game_with_no_snap_count_leaves_the_snap_share_at_the_games_before
FAILED tests/test_rubric.py::test_the_wopr_window_of_a_known_games_week_ends_at_the_week_before_when_the_file_lacks_the_trade_week
5 failed, 180 passed in 13.25s
```
These new tests passed at RED. They guard behavior that already held: the trend reason with two spans, a game with snaps moves the snap share, the WOPR window reads a week 6 row, a missing file is no pending count, slow sources fall back to week N-1.

GREEN:
```
uv run pytest -q tests/test_snapshot.py tests/test_slow_sources.py tests/test_rubric.py
185 passed in 12.91s
```
The first full run then failed the 5 API and live expectations above. After the expectation changes:

## Full suite and ruff

```
uv run ruff check src tests
(no output, exit 0)

uv run pytest -q
1119 passed, 9 deselected in 225.02s (0:03:45)
```

## Ticket criteria

- [x] A week 6 line with targets and points but no snap fields leaves the snap share at the weeks before, never zero (rubric, Nabers).
- [x] The same line moves the target share and the points per game; red zone reads it too.
- [x] The block names snaps pending for the count of such games (`{"snaps": 2}`, `{"snaps": 1}`).
- [x] A player file that lacks the trade week: the window ends at N-1 and the block names usage pending.
- [x] A player file that has the trade week: the window reads it and usage is not pending for that game.
- [x] A line with snaps is pending for nothing and the snap share reads it.
- [x] Every rubric test for a saved week passes unchanged.

## Self-review

- Each changed code file keeps its two-line opening docstring.
- No added line says "live", "partial", or "current week".
- A saved week grades as before. `_wopr` reads only scored weeks through `stats_through`, which is N-1 for a saved week, so extra rows of week N in the WOPR dict change nothing. The pipeline call (`week + 1`) can now hold a row of the week after; nothing reads it.
- The rubric tests import the private `_wopr`, as they already import `_byes_left`.

## Concerns

1. The snap rule differs from the brief wording. See "Why the snap rule reads `tm_off_snp`". A Sleeper line with `tm_off_snp` but no `off_snp` still reads as 0 snaps, in a known game too. The data says that is a real zero.
2. Usage pending is per game: a game is pending when no played player of the game has a week N WOPR row. On a Monday night, a file with the Sunday games names the Monday game pending once it has played lines.
3. The CLI known-games line does not name the pending counts yet. The brief did not ask for it. The stamp text ("usage through week 6") is for the page ticket.
4. The `load_slow_sources` comment "Every grade input ends at the week before `week`, so the expected window does too." is no longer true of every input. I kept it: the expected window part holds, and it is outside this ticket.
5. The `analyze-response.json` fixture now has `pending: {"usage": 8}`. The site repo copy needs the same change (ticket 08).
6. The `_wopr` read costs a second pass of the player file when the file lacks the trade week.

## Fix round 1

The review approved the ticket and asked for three small items.

1. `src/cornerstone/cli.py` `_print_as_of`: the known-games line now names each pending count, for example `Known games of week 6: 14 read, 0 in progress, pending: snaps 9 games, usage 13 games.` A count of 1 says "1 game". With nothing pending, the line stops after the in-progress count.
2. `src/cornerstone/slow_sources.py`: the comment on the expected window is now scoped to that window. It says the window ends at the week before `week`, so it never reads the known games. It also says the expected points file is a Tuesday source and keeps its weekly lag (PRD story 24), unlike the WOPR.
3. `src/cornerstone/snapshot.py` `_pending`: one more docstring line for the per-game against per-player edge. A WR who played with no row keeps a window that ends at N-1, even when a teammate's row keeps his game out of the usage count.

Tests:
- `test_analyze_without_week_grades_the_live_snapshot_and_prints_the_as_of_line` now expects `pending: usage 8 games.` on the line.
- New: `test_the_known_games_line_names_each_pending_count`, with three cases: nothing pending, snaps and usage, and one game.

RED:
```
uv run pytest -q tests/test_cli.py -k "known_games_line or as_of_line"
FAILED tests/test_cli.py::test_analyze_without_week_grades_the_live_snapshot_and_prints_the_as_of_line
FAILED tests/test_cli.py::test_the_known_games_line_names_each_pending_count[pending1-...]
FAILED tests/test_cli.py::test_the_known_games_line_names_each_pending_count[pending2-...]
3 failed, 1 passed, 23 deselected in 2.29s
```

GREEN:
```
uv run ruff check src tests && echo RUFF_OK
RUFF_OK

uv run pytest -q tests/test_cli.py tests/test_snapshot.py
50 passed in 6.52s

uv run pytest -q
1122 passed, 9 deselected in 224.03s (0:03:44)
```
