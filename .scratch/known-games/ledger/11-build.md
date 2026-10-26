# 11 build: a backup with real usage is not a handcuff

Status: done. Branch `known-games-11`, base `0c9940b`. Nothing pushed.

## What I built

1. `carry_share(history, player_id, through)` in `src/cornerstone/history.py`. It gives the percent of his NFL
   team's carries that the player took in his last 3 played games, rounded half up. It gives None with fewer than
   2 played games, with a gap in the stats, or with 0 team carries. The team sum comes from a small helper,
   `_team_total`, that `target_share` now also uses.
2. Three tunables in `src/cornerstone/tunables.py`, each with a why comment: `HANDCUFF_CARRY_SHARE = 30`,
   `HANDCUFF_CARRY_GAMES = 3`, `HANDCUFF_MIN_GAMES = 2`.
3. The gate in `src/cornerstone/adjusters.py`. `_backs_up_a_starter` stays the one handcuff test. It is now
   `_behind_a_starter` (the old depth chart body) and not `_carries_the_ball`. `is_handcuff`, `trade_handcuffs`,
   the sums, the fit, the trend, the expected gap, and the finder all read it, so a freed backup counts everywhere.
4. The handcuff reason. A freed backup gets "X backs up the team's own starter but takes N% of the carries, so
   he counts as a running back." A true handcuff keeps today's words.
5. The glossary "Handcuff" entry states the gate in plain words.

The reason uses the full name, as `named` does for every other reason, not the last name in the ticket example.

## Files changed

- `src/cornerstone/history.py`, `src/cornerstone/adjusters.py`, `src/cornerstone/tunables.py`
- `GLOSSARY.md`
- `tests/conftest.py` (`with_carries` helper), `tests/test_rubric.py`, `tests/test_finder.py`

## TDD evidence

RED, with a stub `carry_share` that returns None:

```
FAILED tests/test_rubric.py::test_the_carry_share_reads_the_last_3_played_games
FAILED tests/test_rubric.py::test_a_backup_at_38_percent_of_the_carries_is_no_handcuff
FAILED tests/test_rubric.py::test_a_known_game_can_lift_a_backup_over_the_carry_gate
FAILED tests/test_finder.py::test_a_backup_with_real_carries_can_go_to_the_roster_of_his_starter
4 failed, 179 passed
```

Before the stub, the rubric module failed at import (`cannot import name 'carry_share'`).
The 15% test and the 1-game and no-carry-data test passed at RED. That is correct: they pin the answer of today.

GREEN: `183 passed` on the two files.

New tests:

- `test_the_carry_share_reads_the_last_3_played_games`: 33, 15, 38, and None with 1 played game.
- `test_a_backup_at_38_percent_of_the_carries_is_no_handcuff`: no handcuff, the reason names 38%, the trend steps -1.
- `test_a_backup_at_15_percent_of_the_carries_is_a_handcuff`: a handcuff, today's reason.
- `test_a_backup_with_1_played_game_or_no_carry_data_keeps_the_depth_chart_answer`.
- `test_a_known_game_can_lift_a_backup_over_the_carry_gate`: the known-games snapshot (bounds 6 and 5) with the
  slow sources. Henderson is at 26% with his real week 6 game, so a handcuff. With 20 week 6 carries he is at 35%,
  so no handcuff, and the reason names 35%.
- `test_a_backup_with_real_carries_can_go_to_the_roster_of_his_starter` (finder).

## Existing tests the gate touched

TreVeyon Henderson is the NE handcuff in four tests. In the fixture he takes 26 of 79 NE carries in weeks 3 to 5,
or 33%, so the gate frees him. These tests keep their purpose with Henderson at 3 carries a game (15%):

- `test_trend_never_steps_down_because_of_a_handcuff`
- `test_expected_gap_of_a_handcuff_does_not_count`
- `test_a_player_who_is_a_handcuff_on_the_roster_that_gets_him_is_never_a_candidate` (finder)

Keaton Mitchell takes 26% of the LAC carries, so the LAC tests did not change.

## Suite and ruff

- `uv run pytest -q`: `1152 passed, 9 deselected in 225.94s`.
- `uv run ruff check src tests`: clean, exit 0.

## Real-data check: the hand-worked week 6 trades

No grade and no reason changed. In all six trades, no traded RB is behind a starter on the roster that gets him,
so the gate never runs on a depth chart backup. All six `test_each_real_week_6_trade_grades_as_worked_by_hand`
cases pass. The handcuff reasons are the same before and after.

## Concerns

1. Brian's case does not pass the gate at 30. In `data/2026`, Blake Corum takes 9 of 20 LAR carries in week 6,
   5 of 23 in week 5, and 5 of 25 in week 4. That is 19 of 68, or 28%. Through week 5 he is at 23%. So Corum
   stays a handcuff at 30. A gate of 25 frees him on the week 6 known games. Brian must decide the number.
2. Weeks 1 and 2 put Corum at 34% and 43%. The 3-game window drops them. That is the rule as written.
3. The gate compares the rounded percent, so 29.5% rounds to 30% and frees the backup. The reason shows the same
   number, so the two agree.
4. `waiver_buckets.py` has its own handcuff list for stashes. I did not change it. It is outside this ticket.

## Fix round 1

### What changed

1. The gate is 25 percent. `HANDCUFF_CARRY_SHARE = 25` in `tunables.py`, with a new why comment: a pure backup sits
   near 15%, and a backup with a real role, such as Corum at 28%, sits above 25%. The glossary "Handcuff" entry
   now says 25%.
2. The gate compares the exact share. `carry_share` now returns the unrounded percent as a float.
   `_carries_the_ball` compares it to the gate. The reason text rounds it half up, so 25.8% shows as "26%".

### Fixture backups at 25

The week 6 fixture has three RBs behind a rostered starter with a gsis_id. The id map fixture lacks many players,
so the tests join these ids by hand.

| Backup | Starter roster | Share, weeks 3 to 5 | At 30 | At 25 |
| --- | --- | --- | --- | --- |
| Keaton Mitchell, LAC | 12 | 25.5% | handcuff | freed |
| Kimani Vidal, LAC | 12 | 14.9% | handcuff | handcuff |
| TreVeyon Henderson, NE | 7 | 32.9% | freed | freed |

Mitchell is now freed. Five tests use him as the LAC handcuff. They now set him to 4 carries a game in weeks 3
to 5, or 12 of 82 (15%), through `_lac_snap` in `test_rubric.py` and an inline `with_carries` in `test_finder.py`.
The Henderson 15% fixtures stay.

The known-games test changed. Henderson's real weeks 4 to 6 give 25 of 96, or 26%, so at 25 he is no handcuff.
The test now sets him to 3 carries in weeks 4 and 5 (13 of 84, 15%). The 20-carry week 6 breakout gives 26 of 97,
or 27%, and the reason names 27%.

`test_the_carry_share_reads_the_last_3_played_games` now pins the exact shares with `pytest.approx`.

### Edge test

`test_the_gate_compares_the_exact_share_and_the_reason_rounds_it`: Stevenson at 29 carries in weeks 3 to 5. At 16
carries Henderson takes 16 of 65, or 24.6%, so he stays a handcuff. At 17 he takes 17 of 66, or 25.8%. He is
freed, and the reason says "26%".

RED with a rounded compare (`_round_half_up(share) >= HANDCUFF_CARRY_SHARE`):

```
E       AssertionError: assert [] == ['12529']
1 failed, 163 deselected
```

GREEN with the exact compare: `184 passed` on `tests/test_rubric.py` and `tests/test_finder.py`.

### Hand-worked week 6 trades

No grade and no reason changed at 25. No traded RB in the six trades is behind a starter on the roster that gets
him. All six cases pass. The letters and steps match `HAND_WORKED`, for example trade 1 is roster 11 A to B and
roster 12 F to D, as before.

### Brian's case on the real data

In `data/2026`, Corum takes 19 of 68 LAR carries in weeks 4 to 6, or 27.9%. At 25 the gate frees him on the
week 6 known games. Through week 5 alone he is at 22.5%, so he stays a handcuff on a week 5 bound.

### Suite and ruff

- `uv run pytest -q`: `1153 passed, 9 deselected in 226.40s`.
- `uv run ruff check src tests`: the first run found two lines over 120. I wrapped them, and that changed only the
  layout. Ruff is now clean, exit 0, and the two files pass again (`184 passed`).
