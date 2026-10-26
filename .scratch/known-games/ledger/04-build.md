# 04 build: the in-progress label

Status: DONE_WITH_CONCERNS. Branch `known-games-04`, base `67f1a4d`. Not pushed.

## What I built

A week N game is in progress when the clock is past its kickoff by less than 4 hours 30 minutes.

- `tunables.py`: `IN_PROGRESS_MINUTES = 4 * 60 + 30`, with a why comment.
- `nflverse.py`: `read_kickoffs(path, season, week)` gives the Eastern kickoff by Sleeper team code. It reads `gameday` and `gametime`. A row with no time, or a file with no `gametime` column, gives no kickoff. `LA` maps to `LAR`.
- `slow_sources.py`: `SlowSources.kickoffs` holds the kickoffs of `week`, the trade week on the live path. It is not in `missing`, because a team with no kickoff counts as final.
- `snapshot.py`:
  - `build_snapshot` takes `now: datetime | None = None`.
  - `_teams_in_progress` gives the game id of each team with a played line (`gp > 0`) whose kickoff is at or before `now` and less than 4 h 30 min before it.
  - `KnownGames.in_progress` counts the distinct game ids.
  - `Snapshot.in_progress_teams: set[str]` holds the team codes. It is on the snapshot, not on the block, so the result and finder documents do not change shape.
  - A saved week passes no trade week, so it has no block and no team in progress.
- `live.py`: `_build_live` takes `now` and passes it on. `live_snapshot` and `live_rosters_snapshot` both pass their `now`.
- `adjusters.py`: `_share_sentences` ends a player's sentence with ", game in progress" when one of his moved shares reads the trade week and his NFL team is in `in_progress_teams`. Both sentence forms carry it, so the label is always the last phrase before the period.
  - Example: `Odunze: snap share 97%, up, over weeks 5 and 6, game in progress.`

The label changes no number and no step. It only edits the text of a sentence the code already writes.

## Which reasons carry the label

- Trend and usage, share sentences: yes.
- Trend and usage, WOPR sentences: no. WOPR is out of scope, and its window ends at N-1 until ticket 03.
- Trend and usage, red zone tiebreak: no. It quotes no number.
- Roster fit: no. The fit reason quotes no week N number. Its only numbers are in the due-back notes, and those are the projection ahead, not a week N stat. See concern 1.

## Files changed

- `src/cornerstone/tunables.py`, `src/cornerstone/nflverse.py`, `src/cornerstone/slow_sources.py`, `src/cornerstone/snapshot.py`, `src/cornerstone/live.py`, `src/cornerstone/adjusters.py`.
- `tests/test_nflverse.py`, `tests/test_snapshot.py`, `tests/test_rubric.py`, `tests/test_live.py`.
- `tests/test_rubric.py`: `_known_games_snap` takes `slow` and `now`, with defaults that keep the old calls the same.

No existing test expectation changed.

## Tests added

- `test_read_kickoffs_gives_the_eastern_kickoff_of_each_team_of_the_week`, `test_read_kickoffs_of_a_file_with_no_game_time_is_empty`.
- Snapshot: 2 hours after a 1 pm kickoff the game is in progress and counts 1. 5 hours after, it counts 0. A game with no schedule row is final. A saved week has no game in progress.
- Rubric: the Odunze sentence ends with "game in progress", and the Watson sentence (no kickoff) does not. The steps and letters are the same with the label on and off, and the label is the only change to the reasons. No reason and no stamp says "live", "partial", or "current week". The analysis prose checks (`_prose_failures`, `_letter_failures` in `cornerstone/analysis.py`) pass on the labeled trend reason and on a comma-joined prose sentence.
- Live: on Monday 2026-10-19 at 9 pm, with an 8:15 pm kickoff for WAS at SF in the schedules cache, the snapshot counts 1 game in progress and the teams `{"WAS", "SF"}`.

## TDD evidence

RED, reader:
```
uv run pytest -q tests/test_snapshot.py tests/test_nflverse.py
E   ImportError: cannot import name 'read_kickoffs' from 'cornerstone.nflverse'
```

RED, snapshot:
```
uv run pytest -q tests/test_snapshot.py
E       TypeError: build_snapshot() got an unexpected keyword argument 'now'
FAILED tests/test_snapshot.py::test_a_game_2_hours_after_its_kickoff_is_in_progress_and_the_block_counts_it
FAILED tests/test_snapshot.py::test_a_game_5_hours_after_its_kickoff_is_final_and_the_block_counts_zero_in_progress
FAILED tests/test_snapshot.py::test_a_game_with_no_schedule_row_is_final - Ty...
FAILED tests/test_snapshot.py::test_a_saved_week_has_no_game_in_progress - Ty...
4 failed, 19 passed in 2.00s
```

RED, rubric:
```
uv run pytest -q tests/test_rubric.py
E       TypeError: build_snapshot() got an unexpected keyword argument 'now'
FAILED tests/test_rubric.py::test_the_trend_reason_of_a_player_whose_known_game_is_in_progress_ends_with_the_label
FAILED tests/test_rubric.py::test_the_adjuster_steps_are_the_same_with_the_label_on_and_off
FAILED tests/test_rubric.py::test_no_reason_and_no_stamp_of_a_game_in_progress_says_live_partial_or_current_week
FAILED tests/test_rubric.py::test_the_prose_checks_of_the_analysis_pass_on_a_reason_with_the_label
6 failed, 141 passed, 3 errors in 12.96s
```
The other 2 failures and the 3 errors came from the helper change in the same run. They pass after the build.

RED, live (after the test, before `now` reached the build):
```
uv run pytest -q tests/test_live.py -k monday
E       AssertionError: assert 0 == 1
FAILED tests/test_live.py::test_on_monday_night_the_clock_of_the_request_puts_the_monday_game_in_progress
1 failed, 1 passed, 26 deselected in 1.29s
```

GREEN:
```
uv run pytest -q tests/test_snapshot.py tests/test_nflverse.py tests/test_rubric.py tests/test_live.py
227 passed, 1 deselected in 18.98s
```

## Full suite and ruff

```
uv run ruff check src tests
RUFF_EXIT=0 (no findings)

uv run pytest -q
1120 passed, 9 deselected in 223.25s (0:03:43)
```

## Real-data check

Monday 2026-10-26, 11:30 ET. `read_kickoffs` on the real schedules cache for week 7 gives 28 teams. The kickoffs run from Thursday 20:15 to Monday 20:15, all at -04:00. I did not run `make analyze`, because no 2026 week 7 game is in progress at 11:30 on a Monday.

## Self-review

- Each changed code file keeps its two-line opening docstring. No comment was removed.
- No new reason, stamp, comment, or docstring says "live", "partial", or "current week". The word "live" stays only in older code names such as `live.py`, which no reason or stamp shows.
- The label never touches a number, a share direction, a step, or a letter. The rubric test checks this.
- The team code for a player comes from `snapshot.players[pid].nfl_team`, the Sleeper player entry. The week N stat row has a `team` too.

## Concerns

1. Roster fit carries no label. The ticket says "the roster fit reason at least". The fit reason says "The best lineup gains after the trade." and quotes no week N number, so the brief rule ("where it quotes a week N points number") gives it no label. The step can still read an in-progress game through the recent points. If the controller wants a label there, the fit reason needs a new sentence that names the players whose lineup value reads a game in progress. That is a new reason shape, so I did not build it.
2. A player who changed NFL teams after his week N game: the label reads his Sleeper player team, not the team of his week N stat row. This is rare. The fix is a set of player ids from the stat rows instead of team codes.
3. The grade cache key does not hold the in-progress count. A grade cached while a game is in progress can serve the label after the game ends, until the cache entry expires or the stat lines change. Ticket 06 owns the key. Adding `as_of.known_games` to the key would close it.
4. The trade facts (for example "Every stat runs through week 6.") get no label. They are facts, not reasons, so the ticket does not cover them.
