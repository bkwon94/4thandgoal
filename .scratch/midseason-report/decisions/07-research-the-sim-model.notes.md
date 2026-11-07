# 07 notes: which sim model runs the rest of the season

Summary: keep the draw of `odds.py`, because its projected shift already reads rest-of-season projections, byes, injuries, return weeks, and the current rosters.
Add the bracket of weeks 15 to 17, full counts of seed, record, and title, and a stored sample of runs. 10,000 runs cost about 0.5 s per client in Python and about 0.13 s in JavaScript.

Measured on 2026-11-05 with the week 8 data of both clients. The script ran with `uv run --exact --package cornerstone` from the worktree root. It lives in the scratchpad, not in the repo.

## 1. How `odds.py` works now

Source: `packages/rankings/python/src/rankings/odds.py`. Tunables: `packages/rankings/python/src/rankings/tunables.py`, lines 17 to 32.

- **Level.** Each run first draws a level for each roster: a normal around the season average, shrunk to the league average (lines 76 to 80, 90). The weight of the roster's own average is n over n + 5, with `LEVEL_SHRINK_WEEKS = 5`. The standard error is spread over the square root of n + 5.
- **Spread.** One spread for the league: the pooled standard deviation of each score from its own roster's average (lines 69 to 75).
- **Week score.** Each remaining week is a normal around the level with the league spread (line 91). The draws of one roster share its level, so a hot run carries over weeks. Two rosters in one week do not correlate.
- **Projected shift.** Each drawn score moves by `PROJECTION_WEIGHT = 0.5` times the gap from the projected best-lineup total of that week to the raw season average (lines 81, 92 to 93, 126 to 138). The shift is a constant. It adds no spread.
- **Inputs.** `scores` (played-week scores), `records` (wins, losses, points for), `remaining` (pairs of weeks N+1 to 14), `projected`, and `client` for spots, byes, and the median game (lines 20 to 50). The caller is `week_odds` and `odds_inputs` in `packages/rankings/python/src/rankings/chapter.py`, lines 82 to 125.
- **Projected totals.** `projected_totals` in `packages/week/python/src/week/sheet/base.py`, lines 86 to 150, reads `projections_ahead.json`, the current `rosters.json`, the NFL bye weeks, and the injury snapshot. It fills the best lineup per week. A starter who is injured and at zero takes the best free player at his slot. It stops at `last_regular_week` (line 103).
- **A week of a run.** `_run` counts the head-to-head win and, for CPC, one more win above the median line (lines 141 to 163, 175 to 184). An exact tie gives no win.
- **Tiebreakers.** Most wins, then most points for, then the lower roster ID (lines 166 to 172). Same as `standings_order`.
- **Runs and seed.** `SIM_RUNS = 5000` (tunables line 19). The seed is `season * 100 + week` (line 64), so one input gives one output.
- **Output.** `TeamOdds` holds playoff odds, bye odds, the modal seed if playoff odds are 50 or more, and a status (lines 110 to 121). The odds clamp to 1 to 99 unless a plain check on wins says in or out (lines 187 to 217). `Swing` splits the runs by each next-week game (lines 101 to 108, 226 to 246).
- **Tests.** `apps/pipeline/tests/test_odds.py` has 34 tests. Some examples: the same seed gives the same odds (line 41), both games count (59), the tiebreakers (69, 76), the bye clamp (100 to 139), the projections (237 to 261), the full league in under 10 s (272), and the week 7 match to the prototype within 3 points (334).

## 2. What the engine lacks for the report

- **The bracket.** The run stops at the regular-season table (line 94). No run plays weeks 15 to 17. So it gives no title odds, no final odds, and no odds of a place.
  - Both leagues: `playoff_teams: 6`, `playoff_week_start: 15`, `playoff_round_type: 0`, one week per round (`clients/<slug>/data/2026/league.json`). Seeds 1 and 2 get the bye (`bracket_byes` in `packages/league/python/src/league/league_settings.py`, line 37).
  - `bracket.json` of week 8 has 7 matches: round 1 has the two games of seeds 3 to 6, round 2 has the bye seeds and a 5th-place game (`p: 5`), and round 3 has the final (`p: 1`) and a 3rd-place game (`p: 3`).
  - NorCal: `playoff_seed_type: 0`. Its round 2 matches carry `t2_from: {w: 1}` and `{w: 2}`, so the bracket is fixed.
  - CPC: `playoff_seed_type: 1`. Its round 2 matches carry no `t2_from`, so the bracket appears to reseed: seed 1 meets the lowest seed left. Check this against the Sleeper league page before the spec.
  - `LeagueSettings` has no field for the reseed rule. Sleeper's rule for a playoff tie is not in the data. Exact float ties are rare, so the higher seed can win a tie.
- **Seed odds.** The run counts each seed (line 85, `seeds`), but the result keeps only the mode (line 114). Return the full count.
- **Final-record odds.** No count of final wins exists. `_run` holds `wins` (line 149) but returns only the order. CPC records count both games, so a CPC final record runs from 0-28 to 28-0.
- **The most likely final table.** The mode of full tables is useless. In 10,000 runs, CPC gave 9,960 distinct tables, and the top table came up 2 times. NorCal gave 9,944, and the top came up 3 times. Even the top 6 in order had 7,974 and 6,974 distinct orders. The report needs a defined table instead, such as the order by mean final wins, or a team-by-seed heat map.
- **A per-run record.** The runs keep no scores. A replay needs each run's drawn scores, or its seed and the parameters to draw them again.

## 3. More inputs, from data the repo holds

| Input | Where it sits now | Cost | Gain |
| --- | --- | --- | --- |
| Rest-of-season projections per player | In: `projections_ahead.json` through `projected_totals` | 0 | Already in the shift |
| Byes | In: a null projection in the bye week, plus `nfl.bye_weeks` | 0 | Already in the shift |
| Injuries and return weeks | In: Sleeper leaves the projection out for each week a player is out, then gives a value from his return week. Example: player 4881, QB, `Out`, no projection weeks 9 to 13, a projection from week 14. | 0 | Already in the shift. The injury snapshot covers the empty weeks with a free player. |
| Roster changes | In: `projected_totals` reads the current `rosters.json` | 0 | Already in. Trades after the build are unknown. |
| Projections of weeks 15 to 17 | In `projections_ahead.json` (weeks 9 to 17, 0.06 MB), but cut at line 103 of `base.py` | Small: one bound | Needed for a bracket draw that knows the playoff roster |
| Spread per roster | Past scores, 8 per roster | Small | Low. 8 scores do not pin a spread, which is why the code pools it (line 69). |
| A draw per player | Projections only, no variance per player | Large: a new model | Low for this report. The lineup-level shift already reads each player. |

No outside source gives a large gain. The current inputs cover the four items the ticket names.

## 4. The cost

Measured, week 8 data, 12 rosters, weeks 9 to 14 left, Apple Silicon:

| Client | 5,000 runs | 10,000 runs | 10,000 runs with the bracket and record counts |
| --- | --- | --- | --- |
| CPC | 0.23 s | 0.46 s | 0.68 s (prototype) |
| NorCal | 0.20 s | 0.40 s | 0.54 s (prototype) |

The timing passed no `projected`. The shift is one add per score, so it costs little. The prototype also gave the title odds and the win counts. Example: CPC roster 3 wins the title in 17.2 % of runs, and NorCal roster 6 in 27.9 %.

Data of a replay, per run: 12 rosters times 9 weeks (6 regular, 3 bracket) is 108 scores.

| Runs stored | JSON, one decimal | Gzip | Binary, uint16 tenths |
| --- | --- | --- | --- |
| 10,000 | 6.3 MB | 2.05 MB | 2.16 MB |
| 100 (estimate, scaled) | 63 KB | about 20 KB | 22 KB |

The bracket pairs and the table follow from the scores, so a run needs no more data. The 10,000-run file is too large for one page. A sample of 100 to 500 runs is small.

## 5. Replay against a live sim in the browser

- **Replay of stored runs.** The page needs a sample of runs, for example 200, about 40 KB gzip. It also needs the aggregate odds of the full 10,000 runs from Python. The page draws nothing. The numbers on the page match the published odds exactly. The reader cannot change a result.
- **Live sim in the browser.** The model is small enough to port: about 60 lines of the run, the median, the tiebreakers, and the bracket. The page needs the mean and standard error of each roster's level, the league spread, the shift per roster per week, the records, the remaining pairs, and the bracket rule. That is under 5 KB.
  - A JavaScript timing port ran 10,000 runs of 9 weeks with the median and the bracket in 126 ms on Node, first run, with a seeded generator. A phone is perhaps 3 to 5 times slower, so about 0.5 s. That is an estimate.
  - A live sim lets the reader pick a winner and see all odds move. The pick fixes the result of one game in each run.
  - Risk: the Python generator `random.gauss` and a JavaScript generator give different draws. The browser odds then differ from the published odds by sample error, about 1 point at 10,000 runs. Two copies of the model can also drift apart. A shared test case with a tolerance guards the drift.
- **Both.** Python publishes the odds and a sample of runs to replay. The browser runs the live model only after the reader picks a winner. Ticket 08 decides the interaction.

## Recommendation

1. Keep the draw of `odds.py` and its inputs. Add the projections of weeks 15 to 17 and a 3-round bracket, fixed for NorCal and reseeded for CPC after a check.
2. Return full counts: each seed, the bye, each final record, the final, and the title. Run 10,000 runs, about 0.7 s per client.
3. Define the "most likely final table" as the order by mean final wins, plus a team-by-seed heat map. Do not use the modal table.
4. Store a sample of about 200 runs for a replay, about 40 KB gzip. Also publish the model parameters, under 5 KB, so ticket 08 can choose a live sim too.
