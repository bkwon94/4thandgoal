# 01: Research notes on the rank measure

## Summary

1. Recommend season points per game, games played only, as the measure of the Position rank inside the grade.
2. Its accuracy ties the current 4-week measure: the hit rate above the line differs by 0.06 or less at each position.
3. It moves players 2 to 3 times less from week to week. At WR the mean move inside the line is 4.0 spots, against 12.1.
4. At week 8 the 4-week measure puts 9 WRs with 2 games or fewer inside the line. Season points per game puts 0 there.
5. The Sleeper weekly projection predicts best, but the repo holds no clean projection snapshot for weeks 1 to 5.

## Method

- Client `cpc`, season 2026. Points are `pts_half_ppr`. The league gives 0.5 per reception and 4 per pass TD (`clients/cpc/data/2026/week-08/raw/league.json`, `scoring_settings`). The repo maps 0.5 to `pts_half_ppr` (`packages/league/python/src/league/league_settings.py:25`).
- The data: the saved weeks 1 to 8 under `clients/cpc/data/2026/history/week-0N/` (`stats.json`, `projections.json`, `matchups.json`). The repo loader `league.history.load_saved_weeks` reads them (`packages/league/python/src/league/history.py:80`). The points of a player come from `player_points`, roster points first, then the stat line (`history.py:112`).
- The rest-of-season projections: `clients/cpc/data/2026/week-06/raw/projections_ahead.json` and `week-07/raw/projections_ahead.json`. Week 8 has a file too, but no later week to score it against.
- The lines: QB 24, RB 36, WR 36, TE 24. `LeagueSettings.lines` sets them (`league_settings.py:120-131`, `GLOSSARY.md:586`). The cpc roster is QB, RB, RB, WR, WR, TE, FLEX, FLEX for 12 teams.
- The script: `/private/tmp/claude-503/-Users-brian-kwon-repos-cpcfantasyfootball/c1703684-42e2-4da7-b339-b6e23181591a/scratchpad/rank_measures.py`. Its output is `out.txt` in the same folder. Run it with `uv run --exact --package cpc-league python <script> <worktree>`.

The measures at week N, for each player at the position with at least one game played through week N:

1. Recent ppg: the points per game over weeks N-3 to N, games played only. This copies `recent_points_per_game` (`packages/league/python/src/league/ranks.py:28-51`, `LINEUP_WEEKS = 4` at `packages/league/python/src/league/tunables.py:8`). A player with no game in the window ranks last, as `rank_table` does (`ranks.py:109-111`). The script leaves out the due-back step of `lineup_value` (`ranks.py:67-79`), because no projection snapshot exists for weeks 1 to 5.
2. Season total: the sum of points through week N.
3. Season ppg: the season total over the games played through week N.
4. Sleeper projection, two forms:
   - 4a: the mean of the weekly projections of weeks N+1 to 14 in `projections_ahead.json`, as `projection_ahead` takes the mean (`ranks.py:54-64`). Only N = 6 and N = 7.
   - 4b: the Sleeper projection of week N+1 alone, from `history/week-(N+1)/projections.json`. It is a stand-in, not a rest-of-season projection. A player on a bye in week N+1 has no row and gets 0.

The scores:

- The target is the real points of weeks N+1 to min(N+4, 8). A missed game counts 0 in the "total" target. The "ppg" target counts only the games played.
- Spearman runs on the relevant pool: each player inside two lines by any of the four measures. Without this cut, hundreds of players at 0 swamp the correlation.
- The hit rate is the share of the top-line players by the measure who are also top-line by the target total.
- The churn is the mean rank move from week N to N+1 of each player inside the line at week N, with the 90th percentile.
- The tables show the mean over N = 5, 6, 7. At N = 4 and below, measures 1 and 3 are the same. The script also prints N = 2 to 7. That range gives the same order.

## Scores

Mean over N = 5 to 7. rho is Spearman. Higher is better for rho and hit. Lower is better for churn. Churn uses the moves from N = 4 to N = 8.

| Pos | Measure | rho, total | rho, ppg | Hit above the line | Churn mean | Churn p90 |
| --- | --- | --- | --- | --- | --- | --- |
| QB | 1 Recent ppg | 0.648 | 0.482 | 0.722 | 5.66 | 10 |
| QB | 2 Season total | 0.694 | 0.611 | 0.778 | 3.04 | 7 |
| QB | 3 Season ppg | 0.607 | 0.481 | 0.681 | 2.59 | 6 |
| QB | 4b Next-week proj | 0.824 | 0.552 | 0.819 | n/a | n/a |
| RB | 1 Recent ppg | 0.523 | 0.676 | 0.676 | 9.13 | 15 |
| RB | 2 Season total | 0.537 | 0.695 | 0.667 | 2.89 | 6 |
| RB | 3 Season ppg | 0.496 | 0.715 | 0.620 | 3.03 | 7 |
| RB | 4b Next-week proj | 0.751 | 0.604 | 0.731 | n/a | n/a |
| WR | 1 Recent ppg | 0.233 | 0.381 | 0.537 | 12.11 | 23 |
| WR | 2 Season total | 0.300 | 0.446 | 0.519 | 4.74 | 10 |
| WR | 3 Season ppg | 0.285 | 0.506 | 0.537 | 4.00 | 10 |
| WR | 4b Next-week proj | 0.599 | 0.384 | 0.639 | n/a | n/a |
| TE | 1 Recent ppg | 0.379 | 0.380 | 0.542 | 6.70 | 15 |
| TE | 2 Season total | 0.426 | 0.452 | 0.569 | 3.10 | 7 |
| TE | 3 Season ppg | 0.366 | 0.427 | 0.569 | 2.85 | 6 |
| TE | 4b Next-week proj | 0.600 | 0.457 | 0.569 | n/a | n/a |

Rest-of-season projection 4a, scored only on players with a row in the file. The line shrinks in proportion to the smaller pool. The week 6 file holds 137 to 167 rows per week. The week 7 file holds up to 513.

| N | Pos | 1 Recent hit / rho | 2 Total hit / rho | 3 Season ppg hit / rho | 4a ROS proj hit / rho |
| --- | --- | --- | --- | --- | --- |
| 6 | QB | 0.33 / 0.00 | 0.33 / -0.13 | 0.17 / -0.42 | 0.33 / -0.20 |
| 6 | RB | 0.40 / 0.44 | 0.60 / 0.47 | 0.53 / 0.39 | 0.53 / 0.43 |
| 6 | WR | 0.33 / 0.34 | 0.33 / 0.26 | 0.44 / 0.28 | 0.56 / 0.39 |
| 6 | TE | 0.33 / 0.09 | 0.33 / 0.03 | 0.67 / 0.11 | 0.67 / 0.24 |
| 7 | QB | 0.50 / 0.28 | 0.50 / 0.33 | 0.50 / 0.27 | 0.50 / 0.28 |
| 7 | RB | 0.59 / 0.55 | 0.59 / 0.53 | 0.59 / 0.53 | 0.59 / 0.57 |
| 7 | WR | 0.36 / 0.41 | 0.39 / 0.47 | 0.39 / 0.44 | 0.43 / 0.48 |
| 7 | TE | 0.47 / 0.52 | 0.58 / 0.53 | 0.47 / 0.54 | 0.47 / 0.54 |

Small samples inside the line at week 8: the players inside the line with 2 games or fewer in the window of the measure.

| Pos | 1 Recent ppg | 3 Season ppg |
| --- | --- | --- |
| QB | 0 | 1 |
| RB | 6 | 2 |
| WR | 9 | 0 |
| TE | 2 | 0 |

What the scores show:

- No measure of the three stat measures wins on accuracy at every position. The order changes with the position and the target. Season ppg against recent ppg differs by 0.06 or less in hit rate. The widest gap is at QB: season total 0.778 against season ppg 0.681, about 2 players of 24.
- Season total does best on the "total" target. That target counts a missed game as 0, so it rewards a player who was healthy in the past. The line asks who is a starter when he plays. The due-back step and the out-for-season step already handle absence (`ranks.py:67-79`).
- Season ppg does best on the "ppg" target at RB and WR, the two positions with a flex share.
- The 4-week measure has 2 to 3 times the churn of the two season measures at every position.
- The next-week projection 4b leads on the "total" target at every position. On the "ppg" target it does not lead, except at TE. So much of its lead likely comes from game-day news: a player ruled out gets a low projection. A grade cannot know that news for weeks after the trade week.
- The rest-of-season projection 4a beats or ties the stat measures at WR. Two weeks of data, with horizons of 2 weeks and 1 week, is too few to judge it.

## Omar Cooper Jr.

Sleeper id `13276`, WR, NYJ, rookie (`week-08/raw/players.json`). His weekly points, from the repo loader:

| Week | Played | Points | Sleeper weekly pos rank | Line |
| --- | --- | --- | --- | --- |
| 1 | yes | 3.5 | 75 | 1 rec, 30 yd |
| 2 to 5 | no | 0 | 999 | active, no snap, no `gp` |
| 6 | yes | 19.3 | 6 | 6 rec, 103 yd, 1 TD |
| 7 | yes | 20.0 | 7 | 5 rec, 115 yd, 1 TD |
| 8 | yes | 0.0 | 999 | 50 of 64 snaps, no catch |

The ranks at week 8 among the WRs in the pool:

- Recent ppg: weeks 5 to 8 hold 3 games, 6, 7, and 8. (19.3 + 20.0 + 0) / 3 = 13.10, which is WR18. Two big games in a 3-game window carry him.
- Season total: 42.8, which is WR60. This matches the Sleeper number in the ticket. The repo `season_rank` sums the same stat lines (`history.py:176-195`), and the script gets WR60 by that sum too.
- Season ppg: 42.8 over 4 games = 10.70, which is WR26.
- Rest-of-season projection at week 8: 7.11 per game, rank 51 of the 180 WRs with a row.

So the 4-week window drops weeks 2 to 5, where he did not play, and keeps only the 3 games that hold both big games. Season ppg keeps his week 1 and his week 8 too, so he falls to WR26, still inside the WR line of 36. The projection puts him near WR51, outside the line. Season total puts him at WR60, because the 4 weeks without a snap count against him.

## Limits

- Only 8 weeks are complete. The horizon at N = 5, 6, and 7 is 3, 2, and 1 weeks. Each N holds 24 to 36 players per line, so a hit rate gap of 0.03 is one player.
- The repo holds a rest-of-season projection snapshot only at weeks 6, 7, and 8 (`week-0N/raw/projections_ahead.json`). Week 8 has no later week to score. So measure 4 as the ticket states it gets only 2 test weeks.
- The row count of `projections_ahead.json` differs by week: 137 to 167 at week 6, up to 513 at week 7. The fetch keeps every player with a projection at the points key (`packages/league/python/src/league/provider/sleeper.py:154-166`). The cause of the small week 6 file is not known.
- The weekly projections in `history/` were saved after each week, so they are the last value before the game. A test of 4b is a stand-in with game-day news, not a projection a grade at week N could read.
- The script leaves out the due-back step of the real Position rank, because it needs a projection snapshot at each week N. That step changes only players due back from an injury.
- The script treats a bye in the target weeks as 0 for every measure, so a bye hurts each measure the same way.
- Sleeper documents no endpoint for stats, projections, or rankings. https://docs.sleeper.com lists User, Avatars, Leagues, Drafts, Players, and Errors only. The repo calls the stats and projections endpoints unofficial (`history.py:28-40`). So "Sleeper sorts by total points" is from the Sleeper app, not from a document. The week 8 total of 42.8 does give WR60, which matches the ticket.

## Citations

- Recent ppg, the window, and the pool: `packages/league/python/src/league/ranks.py:28-51`, `:86-114`.
- The lineup value and the due-back step: `ranks.py:54-79`.
- `LINEUP_WEEKS = 4`: `packages/league/python/src/league/tunables.py:8`.
- The lines: `packages/league/python/src/league/league_settings.py:120-131`, `GLOSSARY.md:586`.
- The points key: `league_settings.py:25`, `history.py:112-116`.
- The season rank by total points: `history.py:176-195`, `GLOSSARY.md:565`.
- The Position rank in the rubric: `packages/analyzer/python/src/analyzer/prompts/rubric.md:65-69`, `GLOSSARY.md:559`.
- The fetch of the projections ahead: `packages/league/python/src/league/provider/sleeper.py:154-166`, `:231`.
- The Sleeper API sections: https://docs.sleeper.com.
