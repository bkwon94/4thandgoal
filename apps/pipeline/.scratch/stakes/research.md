# Research: playoff odds, stakes, and rivalry inputs

Date: 2026-10-23

League id: `1386167364424318976` (`src/cornerstone/pipeline.py:37`). Season 2026, 12 teams.
`$L` below means `https://api.sleeper.app/v1/league/1386167364424318976`.

## 1. Future matchups

Answer: yes. The matchups endpoint returns all 12 entries with `matchup_id` and `roster_id` for
every week we tried, played or not. A future week has `points: 0.0` and every `starters_points`
and `players_points` value at `0.0`. The keys do not change. No league endpoint gives the full
schedule in one call, but a loop over weeks 7 to 14 gives it.

Evidence:

- The code fetches week N and week N+1 only: `matchups` and `matchups_next` in
  `src/cornerstone/sleeper.py:122-123`. The cache is `data/2026/week-06/raw/matchups_next.json`.
  It holds 12 entries, for example `{"points": 0.0, "roster_id": 1, "matchup_id": 2,
  "starters": [...9 ids], "starters_points": [0.0, ...], "players_points": {...: 0.0}}`.
- Live calls on 2026-10-23, `curl -s $L/matchups/{w}` for w = 7, 8, 9, 10, 11, 12, 13, 14, 15,
  16, 17, 18. Each returned 12 entries with keys `custom_points, matchup_id, players,
  players_points, points, roster_id, starters, starters_points`. Weeks 8 to 18 gave
  `points {0.0}`. Week 7 gave a few nonzero points (Thursday game in progress).
- `starters` in a future week holds 9 ids. They look like the current lineup, not a final one.
- The schedule is an 11-week round robin. Weeks 1 to 6 from `data/2026/history/` plus the live
  weeks 7 to 18 show each roster meets 11 distinct opponents in weeks 1 to 11. Weeks 12 to 14
  repeat weeks 1 to 3. For example roster 1:
  `[8, 10, 2, 7, 12, 3, 9, 5, 4, 6, 11, 8, 10, 2 | 7, 12, 3, 9]` for weeks 1 to 18.
- Weeks 15 to 18 also return round-robin pairs (week 18 equals week 7). These are not the
  playoff games. The bracket in fact 2 decides the playoffs.
- The `settings` block of `/league/{id}` has no schedule field. It has `start_week 1`,
  `playoff_week_start 15`, `leg 6`, `last_scored_leg 6` (`data/2026/week-06/raw/league.json`).
- https://docs.sleeper.com documents `matchup_id` as the key that pairs two rosters. It says
  nothing about future weeks; the live calls above are the proof.

## 2. Playoff format

Answer: 6 playoff teams, playoffs start week 15, one week per round, three rounds (weeks 15, 16,
17). Seeds 1 and 2 get a bye. The regular season is weeks 1 to 14. The median game is on. The
code agrees: `PLAYOFF_SPOTS = 6`, `RETURN_BY_WEEK = 14`, `LAST_WEEK = 14`, and
`PLAYOFF_WEEKS = (15, 16, 17)`.

Evidence, from `data/2026/week-06/raw/league.json` `settings`:

| Field | Value |
| --- | --- |
| `playoff_teams` | 6 |
| `playoff_week_start` | 15 |
| `playoff_type` | 0 |
| `playoff_round_type` | 0 |
| `playoff_seed_type` | 1 |
| `league_average_match` | 1 |
| `start_week` | 1 |
| `trade_deadline` | 11 |
| `num_teams` | 12 |

- Bracket: `data/2026/week-06/raw/bracket.json`, and the live `curl -s $L/winners_bracket`
  gives the same rows. Round 1 (`r: 1`): `t1: 9 v t2: 2` and `t1: 1 v t2: 6`. Round 2: `t1: 3`
  and `t1: 5` wait for a winner, so rosters 3 and 5 (the top two seeds now) have byes. Round 3:
  `p: 1` (final, `t1_from {w: 3}`, `t2_from {w: 4}`) and `p: 3` (third place). A `p: 5` game
  sits in round 2.
- Three rounds after week 14 means weeks 15, 16, 17. `playoff_round_type 0` fits one week per
  round, but the Sleeper docs do not define the codes. The bracket shape is the proof.
- The bracket already fills round 1 with roster ids from the current standings. Its seed
  order (3, 5, 6, 9, 2, 1) matches the code's `standings_order` exactly (see fact 3).
- A `losers_bracket` exists too (`curl -s $L/losers_bracket`): rosters 12 v 10, 8 v 11, byes for
  4 and 7.
- Code: `src/cornerstone/tunables.py:34` `PLAYOFF_SPOTS = 6`; `:39` `RETURN_BY_WEEK = 14`
  ("The last week of the regular season"); `src/cornerstone/sheet.py:53-54` `FIRST_WEEK = 6`,
  `LAST_WEEK = 14` (a later week is "a playoff week", `sheet.py:156-159`);
  `src/cornerstone/nflverse.py:83` `PLAYOFF_WEEKS = (15, 16, 17)`;
  `src/cornerstone/prompts/rubric.md:147` "opponents in weeks 15 to 17".
- The 2025 league (`previous_league_id 1221493709036584960`) had the same 6 teams and week 15
  start, but `league_average_match 0` (no median game) and `playoff_seed_type 0`.

## 3. The median game

Answer: each week is two games. A team wins the median game when its score is above the week
median, loses when below, and neither on an exact tie. The median is the mean of the 6th and
7th scores. Sleeper's roster `settings.wins` and `losses` already include the median game, and
they match the code's own count for every team. The order is wins, then points for. No head-to-
head tiebreak exists in the code, and the Sleeper bracket does not use one either.

Evidence:

- `src/cornerstone/facts_league.py:46-71` `season_records`: per week, `settle` the pair game,
  then `settle(rid, score, median)` for the median game. A tie adds to neither wins nor losses
  (`:56-60`). There is no tie counter.
- `facts_league.py:474-478` `week_median`: `(ordered[5] + ordered[6]) / 2` in `Decimal`.
  `facts_matchup.py:107-121` uses the same rule for the page.
- `facts_league.py:74-79` `standings_order`: sort by `(-wins, -points_for)`. The standings and
  the power rankings both use it. A tie on wins and points for keeps dict order.
- `facts_league.py:82-90`: standings come from history when it is complete, and fall back to
  `rosters.json` wins and losses otherwise (`parse.py:30` reads `fpts + fpts_decimal / 100`).
- `power_rankings.py` `_week_games` (line 92): the head-to-head game first, then the
  median game. `_form_streak` (line 107) counts back from the newest game, so the median
  game is the newer game of its week. A 0 result (tie) ends the streak.
- `facts_league.py:460-471` `_streak` and `power_rankings.py:86` `_head_to_head_record` count the
  head-to-head game only.
- Check (`uv run python`, `season_records` over `data/2026/history` weeks 1 to 6, against
  `data/2026/week-06/raw/rosters.json`): all 12 rosters match on wins, losses, and points for.
  Example: roster 3 `(10, 2, 739.67)`, Sleeper `10 2 739.67`. The Sleeper string
  `metadata.record` is two letters per week, head-to-head then median. Roster 3 is
  `WWWWWWLLWWWW` in both the code and Sleeper.
- Tiebreak check: rosters 9 and 2 are both 7-5. Roster 2 beat roster 9 in week 4, but roster 9
  (698.30 points for) is seeded above roster 2 (611.71). Rosters 1, 8, 10 are all 6-6. Roster 1
  lost to roster 10 in week 2, but roster 1 (685.01) holds the 6th seed. So the bracket uses
  points for, not head to head, as the first tiebreak. The meaning of `playoff_seed_type 1` is
  not documented.
- Week medians, weeks 1 to 6: 111.36, 96.34, 107.135, 104.575, 107.345, 106.825.

## 4. Scoring model inputs

Answer: the history holds one total score per roster per week, for weeks 1 to 6 of 2026 only.
So each team has 6 weekly scores today, 72 in the league. Per-player points let you get bench
points. Per-player projections exist, but no team projection; you must sum the starters. The code
computes mean, high, low, and a 3-week mean per team. It computes no standard deviation.

Evidence:

- Files: `data/2026/history/week-01` to `week-06`, each with `matchups.json`, `projections.json`,
  `stats.json`, `transactions.json` (`HISTORY_FILES`, `history.py:19`). Week 6 also has
  `injuries.json`. No other season folder exists under `data/`.
- `matchups.json` row keys: `custom_points, matchup_id, players, players_points, points,
  roster_id, starters, starters_points`. Keyed by `roster_id`, not by owner.
- `parse_past_week` (`parse.py:172-203`) gives `PastWeek` (`models.py:112-125`):
  `scores: dict[roster_id, float]`, `pairs: list[(a, b)]`, `points: dict[player_id, float]`,
  `projections: dict[player_id, float]` (`pts_half_ppr`), `stats`, `moves`, `trades`,
  `positions`, `nfl_teams`. `History` is `week` plus `weeks: dict[int, PastWeek]`
  (`models.py:138-145`).
- Bench points: `players` minus `starters`, with `players_points`. The `PastWeek` model drops
  `starters`, so a bench total needs the raw file or a model change.
- Projections: `projections.json` is per player. A team projection is the sum over `starters`.
  Future weeks have no projection in the cache; `fetch_week` saves only week N projections.
- `rosters.json` `settings.ppts` holds max potential points per roster (season to date).
- Week 7 is not yet in history. The build saves each week after the page (`pipeline.py:274-278`).
- Existing per-team stats: `facts_league.py:431-457` `_full_season_history` gives `high`,
  `low`, `average`, `trend` (mean of the last `TREND_WEEKS = 3`), `weeks_over` 100, 110, 120,
  `new_high`, `new_low`, `streak`. `power_rankings.py` gives the all-play rate and the mean
  head-to-head margin. No variance or standard deviation exists in `src/`.
- With 6 points per team, a normal fit per team rests on 6 values. The league pool has 72.

## 5. Where the facts land

Answer: a fact is `Fact(id, text, numbers, teams, players)` (`models.py:280-285`). The sheet
builds every fact family into one dict, and each `Chapter` lists the fact ids it may cite. The
writer prompt lists `- {fid}: {text}`, and the verifier checks each number in a sentence against
the `numbers` of the cited facts. `rankings.json` comes from `render_rankings` in the Python repo.
An odds number would fit as a new fact family, a new rankings row field, and a new column.

Evidence, Python repo:

- Fact ids: `S.{rank}` standings (`sheet.py:321-342`), `NX.{a}v{b}` next week
  (`sheet.py:542-555`), `SOS.{roster_id}` next-opponent win rate (`sheet.py:583-596`),
  `MED.*`, `M{matchup_id}.*`, `PICK`, `AW.*`, `RANK.*`, `LEAD.*`, `H.{rid}.{kind}`, `PR.{rid}`,
  `W.*`, `D.*`, `I.*`. All families join in `build_bundle` (`sheet.py:1251-1256`).
- `S.` text: `"{team} is {rank} with a {w-l} record and {pf} points for, {place}."`. A team on
  the cut wins gets a fixed phrase from `CUT_PHRASES` (`sheet.py:88-94`, `cut_phrase` at
  `:310-318`). Others get `"in|out of the playoff spots, N game(s) above|below the cut"`.
  Example: `S.7` "Return of T Mac is 7th with a 6-6 record and 618.97 points for, 1 spot
  outside the playoff spots." (`data/2026/week-06/facts.json`).
- `Nums` (`sheet.py:163-193`) records every number put in the text, so `numbers` is exact.
- Next week today: `next_week` (`facts_league.py:216-244`) scores each pair on table position
  and stakes (`_stakes_signal`: either team within 1 game of the cut). The top two are "Must
  Watch". Fact text: "Next week Lil Fridge (10-2, 1st) plays Return of T Mac (6-6, 7th). Must
  Watch: 1st vs 7th, near the playoff cut." The `next_week` chapter cites `NX.`, `S.`, `SOS.`,
  and `H.*.streak` and `H.*.trend`, in 1 to 2 sentences (`sheet.py:76, 1232-1237`).
- `SOS` reads only the next opponent; the docstring says "Version 1 has only the next one"
  (`facts_league.py:116-128`).
- Writer: `build_writer_prompt` (`writer.py:156-171`) lists the chapter's facts.
- Verifier: `code_check` (`verifier.py:242-290`) fails a fact id not in the chapter and any
  number not in the cited facts' `numbers`. `build_verifier_prompt` (`verifier.py:348-370`)
  gives the Claude check the same fact lines.
- `rankings.json`: `pipeline.py:280-307` `_write_rankings` calls `render.py:298-339`
  `render_rankings`, which writes `site/2026/rankings.json`. `publish.py:62-66` copies it to the
  site repo. Schema (`RANKINGS_SCHEMA_VERSION = 1`, `render.py:30`):
  `{schema_version, season, weeks: [{week, rows: [{roster_id, name, wins, losses, rank,
  movement, components: {standing, form, schedule_played, scoring}, blurb: [{text,
  fact_ids}]}]}]}`. The file holds weeks 1 to 6 now.

Evidence, site repo `~/repos/cpcfantasyfootball` (main at `20170b6`, no other worktrees):

- `src/lib/rankings-types.ts:13-31` mirrors the schema; `schema_version: 1`.
- `src/lib/rankings-data.ts:13-35` `loadRankings` reads `public/{season}/rankings.json` and
  throws on a schema mismatch. A new field needs a version bump on both sides, or an optional
  field under version 1.
- `src/app/rankings/page.tsx` renders the last week with `PowerRankings`.
- `src/components/rankings/power-rankings.tsx` columns: `#`, `+/-`, `Team`, `W-L`, then
  `Stand`, `Form`, `Sched`, `Pts` from the page width up (`COMPONENTS`, lines 18-23; `GRID`,
  line 33). On a phone the four components move into the open row (`ComponentCells`, 62-73),
  which also holds the blurb (133-141).
- An odds column would go after `W-L` in `GRID` and the header (154-170), plus one cell in `Row`
  (87-97). A per-team odds line fits in the open row beside `ComponentCells` or the blurb.
- `src/lib/rankings.ts` holds `biggestMover` only.

## 6. Head-to-head history

Answer: for 2026, yes. `history.py` holds every 2026 game with both scores, so a 2026 head-to-
head record and margin need no fetch. All-time needs a fetch. The cache has only 2026, and the
2025 league is on the API. Owner ids are stable user ids, but roster ids change between seasons.
No pair helper exists.

Evidence:

- `PastWeek.pairs` and `PastWeek.scores` hold both sides of every game, weeks 1 to 6, 6 pairs
  each (`uv run python`: `{1: 6, 2: 6, ...}` pairs, 12 scores per week).
- Only `data/2026/` exists. `league.json` `previous_league_id` is `1221493709036584960`.
  `curl -s https://api.sleeper.app/v1/league/1221493709036584960` gives season 2025,
  status `complete`, `previous_league_id: null`. So 2025 is the only earlier season on Sleeper.
- Roster to owner, 2025 versus 2026 (`/rosters` of each league): 9 of 12 roster ids keep the
  same owner. The owner of 2026 roster 3 (`1265387184765014016`) was roster 12 in 2025. 2026
  rosters 11 and 12 have new owners. 10 owners are in both seasons. A rivalry key must be
  `owner_id`, not `roster_id`. `co_owners` is null on every 2026 roster.
- 2025 had no median game (`league_average_match 0`), so each 2025 week holds one game per team.
- Helpers: `facts_league.py:481-492` `head_to_head(week, roster_id)` gives one week's opponent
  and result. `power_rankings.py` `_head_to_head_record` gives one team's record against all.
  No function returns the record or margin between two teams. No "rival" match in `src/`.

## Open points

- The Sleeper docs do not define `playoff_type`, `playoff_round_type`, or `playoff_seed_type`
  codes. The bracket shape and seed order are the proof used here.
- The data does not show what Sleeper does with the round-robin pairs of weeks 15 to 17 once the
  playoffs start. Do not read them as playoff games.
- The data does not show the full Sleeper seed tiebreak past points for. No two teams are tied
  on both wins and points for, so the next rule is not visible.
- Future-week `starters` may change before kickoff. Use only `matchup_id` and `roster_id`.
- 2025 history (scores and pairs) is not cached. A rivalry over all time needs
  `fetch_past_week` (or a new loop) against the 2025 league id.

## Baseline

Tunables in `src/cornerstone/tunables.py`:

| Name | Value |
| --- | --- |
| `BAND_A`, `BAND_B`, `BAND_C`, `BAND_D` | 1.25, 1.10, 0.90, 0.75 |
| `START_LETTER_BANDS` | the four bands with A to D |
| `CONSOLIDATION_MARGIN` | 1.25 |
| `LINEUP_WEEKS` | 4 |
| `FIT_THRESHOLD` | 3.0 |
| `PLAYOFF_SPOTS` | 6 |
| `SELLER_GAP` | 2 |
| `RETURN_BY_WEEK` | 14 |
| `SHARE_WEEKS` | 2 |
| `INJURY_WEEKS` | 3 |
| `RETURN_WINDOW_WEEKS` | 2 |
| `SCHEDULE_RANK_GAP` | 4 |
| `CLAMP_STEPS` | 1 |
| `ACCEPT_AT_OR_ABOVE`, `DECLINE_AT_OR_BELOW` | "B", "D" |
| `WIN_WIN_AT_OR_ABOVE`, `LOPSIDED_AT_OR_BELOW` | "B", "D" |
| `RATE_LIMIT_PER_MINUTE` | 10 |
| `GRADES_PER_MINUTE`, `GRADES_PER_DAY` | 5, 20 |
| `TEAMS_CACHE_SECONDS` | 300 |
| `FINDER_TOP` | 3 |
| `POWER_WEIGHTS` | 0.25 each for standing, form, schedule_played, scoring |

Other constants: `TREND_WEEKS = 3`, `TEAM_COUNT = 12`, `WEIGHTS` for the Matchup of the Week
(`facts_league.py:30-37`); `FIRST_WEEK = 6`, `LAST_WEEK = 14` (`sheet.py:53-54`).

Tests: `uv run pytest -q` on 2026-10-23 gave `765 passed, 8 deselected in 100.43s`.
