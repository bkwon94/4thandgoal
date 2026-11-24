# 02 notes: the seed tiebreak of Sleeper and of the sim

Ticket: `.scratch/playoff-paths/decisions/02-research-tiebreak-rules.md`. Research date: 2026-11-24.

## 1. The Sleeper rules

Sources, in order of trust:

- S1. Sleeper support, "How do playoff teams get determined?": https://support.sleeper.com/en/articles/2203518-how-do-playoff-teams-get-determined
- S2. Sleeper support, "Can I set tiebreakers?": https://support.sleeper.com/en/articles/4238872-can-i-set-tiebreakers
- S3. Sleeper blog, "What Happens If You Tie in Fantasy Football?": https://sleeper.com/blog/what-happens-if-you-tie-fantasy-football/
- S4. Sleeper API docs: https://docs.sleeper.com/
- S5. The real league data: `clients/<slug>/data/2026/week-NN/raw/{rosters,bracket}.json`. Sleeper wrote these files.

Rules:

1. **The seed order is Overall Record, then Points For, then higher Points Against.** S1 says: "To determine seeding, we look at the following in this order: Overall Record, Points For, Higher Points Against." S2 says: "If that is also tied, the team with the higher Points Against will advance."
2. **A tie past Points Against is a coin flip.** S2: "Any additional tiebreakers are determined by a coin flip unless the commissioner manually adjusts playoff seeding." No head-to-head rule exists. A head-to-head rule is only a manual custom seed (S1, S2).
3. **A regular-season game can end in a tie.** S2: "you'll just get a tie added to your record." S3: "3-1, then ties in Week 5, its record would become 3-1-1." No source says how a tie ranks against a win or a loss in the Overall Record.
4. **A tied playoff game goes to the higher seed.** S2 and S3 say this.
5. **Divisions change the seeds.** S1 gives the division winners the top seeds. Both leagues have no divisions: cpc has `divisions: 0`, and NorCal has no `divisions` key. So this rule does not apply.
6. **No tiebreak setting exists in the data.** Neither `league.json` has a tiebreak key. S4 does not define `playoff_seed_type` or `league_average_match`. It shows the league `settings` only as "{ settings object }".

The settings of each league (`clients/<slug>/data/2026/league.json`):

| Key | cpc | NorCal |
| --- | --- | --- |
| `playoff_seed_type` | 1 | 0 |
| `league_average_match` | 1 | 0 |
| `divisions` | 0 | absent |
| `playoff_teams` | 6 | 6 |
| `playoff_week_start` | 15 | 15 |

**`playoff_seed_type` is not a tiebreak setting.** No Sleeper source defines it. The bracket files show the meaning. NorCal (0) has `t2_from: {w: 1}` and `{w: 2}` in round 2, so its bracket is fixed. cpc (1) has no `t2_from` in round 2, so its bracket reseeds. The repo already reads it this way: `packages/league/python/src/league/provider/sleeper.py:383` sets `reseed=settings.playoff_seed_type == 1`. A third-party PR gives the same reading (https://github.com/datadrivenfootball/fantasy-tools/pull/1469, low trust). The seed tiebreak is the same for both values: the data below shows the same order rule in both leagues.

## 2. The median game counts in the record

Yes. With `league_average_match: 1`, Sleeper puts the median game in `settings.wins` and `settings.losses` of each roster. So the median game counts in the Overall Record of rule 1.

Proof from cpc week 10 (`clients/cpc/data/2026/week-10/raw/rosters.json`):

- The wins of all 12 rosters sum to 120. Ten weeks of two games for 12 teams give 120 wins. Head-to-head games alone give 60.
- For each roster, the head-to-head wins plus the wins above the week median from `history/week-01` to `week-10` equal `settings.wins`. All 12 match. Example: roster 3 has 7 + 6 = 13, and Sleeper has 13.
- `metadata.record` of each roster has 20 letters after 10 weeks, two per week.

S1, S2, and S3 do not mention the median game. The data is the only source for this answer. It agrees with `.scratch/stakes/pipeline/research.md` section 3.

## 3. How the sim orders teams

- `packages/sim/python/src/sim/season.py:306`: `table = sorted(rosters, key=lambda rid: (-wins[rid], -points[rid], rid))`. The first `spots` entries are the seeds (line 308).
- `wins` and `points` come from `_regular` (`season.py:553-590`). A head-to-head win and a score above the median line each add one win (lines 564-573). An exact tie adds no win (docstring, line 558).
- The start records come from `season_records` in `packages/league/python/src/league/standings_table.py:35-64`. They are `(wins, losses, points_for)`. "A tie in a game counts as neither a win nor a loss." No tie count and no points against exist in the tuple.
- The same key is in `packages/sim/python/src/sim/page.py:221`: `(-records[rid][0], -records[rid][2], rid)`.
- The standings page uses `standings_order` in `standings_table.py:72`: `(-records[rid][0], -records[rid][2])`, with no third key. Python's sort is stable, so an exact tie keeps the dict order.
- A tied bracket game goes to the higher seed: `_winner`, `season.py:647-652`. This matches rule 4.

## 4. A test on the real standings

I sorted each stored `rosters.json` with the sim key and compared the result with the seeds in the `bracket.json` of the same week. The bracket rows map to seeds this way: round 1 match 1 is seed 4 (`t1`) against seed 5 (`t2`), round 1 match 2 is seed 6 (`t1`) against seed 3 (`t2`), and round 2 `t1` of matches 3 and 4 is seed 1 and seed 2.

| League, week | Sim seeds 1 to 6 | Sleeper seeds 1 to 6 | Match |
| --- | --- | --- | --- |
| cpc 6 | 3, 5, 6, 9, 2, 1 | 3, 5, 6, 9, 2, 1 | yes |
| cpc 7 | 3, 6, 5, 2, 9, 1 | 3, 6, 5, 2, 9, 1 | yes |
| cpc 8 | 2, 3, 6, 5, 9, 1 | 2, 3, 6, 5, 9, 1 | yes |
| cpc 9 | 2, 6, 5, 3, 1, 8 | 2, 6, 5, 3, 1, 8 | yes |
| cpc 10 | 3, 2, 5, 9, 1, 6 | 3, 2, 5, 9, 1, 6 | yes |
| NorCal 8 | 6, 1, 9, 8, 10, 11 | 6, 9, 1, 8, 10, 11 | **no** |
| NorCal 9 | 6, 8, 1, 10, 11, 9 | 6, 8, 1, 10, 11, 9 | yes |
| NorCal 10 | 8, 1, 6, 10, 5, 11 | 8, 1, 6, 10, 5, 11 | yes |

Each cpc week has ties on wins, up to five teams at 11-7 in week 9. Points For breaks each one the same way in both orders.

**NorCal week 8 is the one miss.** Rosters 1 and 9 are both 5-3 with exactly 1010.86 Points For (`fpts` 1010, `fpts_decimal` 86). Points Against is 978.84 for roster 1 and 980.30 for roster 9. Sleeper seeds roster 9 second, with the bye, and roster 1 third. That is rule 1: higher Points Against wins. The sim key falls to `rid` and puts roster 1 second. Head-to-head does not explain it, because rosters 1 and 9 did not meet in weeks 1 to 8.

## 5. The gaps between the sim and Sleeper

1. **No Points Against tiebreak.** The sim and the standings break an exact Points For tie by `rid` (sim) or by dict order (`standings_order`). Sleeper uses higher Points Against. The real data hit this case once, in NorCal week 8. Inside a run the drawn scores are floats, so an exact Points For tie almost never happens. The gap matters for the real table now and for the last regular week once points are set.
2. **No coin flip past Points Against.** The sim uses the lowest `rid`. Sleeper uses a coin flip. A fixed rule is a fair stand-in, but the page must not claim that the lower `rid` wins.
3. **A tied game has no place in the record.** The sim and `season_records` count a tie as neither win nor loss, and they sort by wins only. So a 5-4-1 team ranks with a 5-5 team. Sleeper adds a tie to the record (rule 3), but no source says how it ranks. No stored week has a tie (`ties` is 0 on each roster), so the data cannot show the rule. This gap is open.
4. **Manual custom seeds.** A commissioner can change the seeds by hand (S1, S2). Nothing in the API data shows a custom seed except the bracket itself. The sim cannot model it.

## 6. Recommended decision

The sim order is right for each real case but one: wins with the median game, then Points For, as Sleeper does. Add higher Points Against as the third key in `season.py:306`, `page.py:221`, and `standings_order`, then keep `rid` as the last fixed stand-in for the coin flip. This needs Points Against in the records tuple, and the NorCal week 8 table gives a real test case. Treat a tied game as an open edge: say in the copy that the order assumes no tied games, and leave the rule for a tie in the record to a later ticket.
