# 03: The game story data check

Spec: `.scratch/week-8-fixes/PRD.md`, part 3.

**What to build:** A report, not code. Find out what the saved week 8 data holds for a game story: each
player's injury status and when it changed, the timing of scores within the week (Thursday, Sunday early,
Sunday late, Monday night), and the Monday night result as a turn in a matchup. Say what is there, what is
not, and what one fetch would add. Write the report under `## Report` in this ticket.

**Blocked by:** none. Tickets 04 and 05 wait on this one.

**Status:** ready-for-agent

- [x] List the saved files of week 8 under `data/2026/week-08/` and `data/2026/history/week-08/`, with one line each on what it holds.
- [x] Injuries: which file holds a player's injury status, and does the data say when it changed?
- [x] Timing: does any saved file give a game's day or kickoff, so a score can be placed on Thursday, Sunday, or Monday? Check the nflverse files too.
- [x] Monday night: can the data say which matchups were open before Monday night and which flipped?
- [x] For each gap, name the one fetch that would fill it, its source, and its cost. Prefer a source the provider already reaches.
- [x] Recommend the smallest set of facts for ticket 04, as a list of fact names with their source file.
- [x] Close with the files-read line.

## Report

All paths are from the pipeline repo root. "Raw" means `data/2026/week-08/raw/`. "Cache" means
`data/cache/nflverse/`. The cache is in `.gitignore`, so a fresh worktree has no cache. I read the cache of the
main checkout, read-only, from the downloads of 2026-11-03 08:06.

### 1. The saved files of week 8

`data/2026/week-08/`:

- `facts.json`: the build output. Keys `data`, `sheet`, `odds`, `waiver`. `sheet.facts` holds 592 facts by id.
- `blurbs.json`: the written text of each chapter. Keys `motw`, `recap_1` to `recap_6`, `awards`, and others.
- `verify.json`: the verifier result. Keys `build`, `chapters`.
- `raw/state.json`: the Sleeper NFL state at fetch time. Sample: `"week": 9, "display_week": 8`.
- `raw/fetched.json`: the fetch time of the transactions. Sample: `"2026-11-03T08:05:54-05:00"`.
- `raw/league.json`: the league settings and the scoring. Sample: `scoring_settings.rec` is `0.5`.
- `raw/users.json`: the 12 managers. Keys `user_id`, `display_name`.
- `raw/rosters.json`: the 12 rosters at fetch time. Keys `roster_id`, `owner_id`, `starters`, `players`.
- `raw/matchups.json`: the final week 8 score of each roster. Keys `matchup_id`, `points`, `starters`,
  `starters_points`, `players_points`. It holds final totals only, with no time.
- `raw/matchups_next.json`: the week 9 pairs, same keys.
- `raw/schedule.json`: the pairs of weeks 10 to the last regular week. Keys `week`, `matchups`.
- `raw/stats.json`: 681 player stat lines of week 8. Keys `player_id`, `team`, `opponent`, `game_id`, `date`,
  `stats`, `player`. Sample: `date` is `"2026-10-29"` for 49 lines, `"2026-11-01"` for 581, `"2026-11-02"` for 51.
- `raw/projections.json`: 3302 projection lines of week 8, the same keys as `stats.json`.
- `raw/projections_ahead.json`: the projections of weeks 9 to 17. Keys `week`, `projections`.
- `raw/players.json`: the Sleeper players file, 12229 players, at fetch time. It holds `injury_status`,
  `injury_body_part`, `injury_start_date`, `injury_notes`, `practice_participation`, `news_updated`.
- `raw/transactions.json` and `raw/transactions_prev.json`: the moves of week 8, and of week 7 fetched again.
- `raw/trending.json`: the top 50 adds across Sleeper in the last day. Keys `player_id`, `count`.
- `raw/bracket.json`: the playoff bracket. Keys `r`, `m`, `t1`, `t2`, `w`, `l`.
- No `raw/nflverse.json`. `pipeline.py` saves the extract only when every source is complete, so week 8 has
  no saved nflverse extract.

`data/2026/history/week-08/`:

- `matchups.json`, `stats.json`, `projections.json`, `transactions.json`: copies of the raw files.
- `injuries.json`: 35 rostered players with a status, as `player_id` to status. `history.py`
  `_save_injuries` writes it from `players.json` `injury_status`. Sample: `"4881": "Out"`. It has no body part
  and no date. Weeks 1 to 5 have no `injuries.json`. Weeks 6, 7, and 8 have one.

### 2. Injuries

- **The status now:** `raw/players.json` `<player_id>.injury_status` and `.injury_body_part`. Sample:
  `"4881"` (Lamar Jackson) is `"Out"`, `"Thumb"`. The sheet already says it as `M6.inj.4881`: "Lamar Jackson
  is now listed Out (Thumb) on Sleeper as of the Tuesday after this week's games. The status may have come
  from this game."
- **The status before the game:** the cache `injuries_2026.csv.gz`, the nflverse weekly report, read by
  `nflverse.read_injuries`. Columns `week`, `gsis_id`, `report_status`, `practice_status`. Sample: Lamar
  Jackson week 8 has `report_status` empty and `practice_status` "Full Participation in Practice". Week 7 has
  `report_status` "Out", injury "Ankle". The sheet uses it as `I.<player_id>.pregame` and `.history`.
- **The status one week earlier:** `data/2026/week-07/raw/players.json` `"4881"` is `"Out"`, `"Ankle"`.
  `history/week-07/injuries.json` gives `"4881": "Out"` only, so the history file cannot show the new injury.
  Only the body part in the two raw `players.json` files shows it: Ankle, then Thumb.
- **When it changed:** the saved Sleeper data does not say. `injury_start_date` is null for all 12229 players.
  `news_updated` is the time of the last news item, not of the status change. Sample: `"4881"` is
  `1793666149623`, which is 2026-11-03 00:35 UTC.
- **The in-game proof:** the cache `play_by_play_2026.csv.gz` holds it. Game `2026_08_BAL_BUF`, `qtr` 1,
  `time` 10:04, `time_of_day` `2026-11-01T18:15:38.780Z`, `desc` "L.Jackson pass incomplete short right to
  4-Z.Flowers ... L.Jackson was injured during the play". `raw/stats.json` agrees: `"4881"` has `off_snp` 1 of
  `tm_off_snp` 51, `pass_att` 1, 0 points on a 20.52 projection.

### 3. Timing

- **The day:** `raw/stats.json` `<line>.date` and `.game_id` give the day of each player's game. Sample:
  `game_id` `"202610812"`, `team` `"GB"`, `date` `"2026-10-29"`, a Thursday. This splits Thursday, Sunday, and
  Monday with no other file.
- **The kickoff:** the cache `games.csv` columns `gameday`, `weekday`, `gametime`, in Eastern time.
  `nflverse.read_kickoffs` reads it, and `slow_sources.py` loads it as `SlowSources.kickoffs`. Now only the
  in-progress label of `snapshot.py` reads it. Sample: `2026_08_CAR_GB`, Thursday, 20:15. Week 8 has 1
  Thursday game, 8 Sunday games at 13:00, 3 at 16:05 or 16:25, `PHI@WAS` at 20:20, and `CHI@SEA` Monday 20:15.
- **The play time:** the cache `play_by_play_2026.csv.gz` columns `time_of_day`, `qtr`, `time`, `desc`. All
  14 week 8 games are in it, 2453 plays. `nflverse_usage.PLAY_COLUMNS` does not keep these columns now.
- **The lead after each slot:** I rebuilt it from `raw/matchups.json` `starters` and `starters_points`, with
  the slot from `raw/stats.json` `team` and `games.csv`. The sum of `starters_points` equals `points` for all
  12 rosters. Each roster's lead, as the margin after each slot:

| Matchup | Thu | Sun early | Sun late | Sun night | Mon | Lead changes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 Lil Fridge v Maye d'force B with U | LF +2.76 | M +17.74 | M +46.25 | M +34.95 | M +41.05 | 1 |
| 2 Return of T Mac v behold the lamb | R +45.62 | R +39.21 | R +19.71 | R +26.21 | R +26.21 | 0 |
| 3 The Blue Tent v London Cooking | LC +8.10 | LC +8.69 | BT +6.11 | LC +3.67 | BT +1.43 | 3 |
| 4 All You Need Is Love v Unsolicited Dak Picks | U +21.80 | A +56.73 | A +43.53 | A +16.28 | A +24.28 | 1 |
| 5 NFC Least v Teehee | 0 to 0 | T +62.52 | T +71.62 | T +59.72 | T +49.02 | 0 |
| 6 Bo Girds v To Infinity and Bijan | BG +17.40 | TI +14.85 | TI +38.59 | TI +30.69 | TI +30.69 | 1 |

- **Inside a slot:** the saved Sleeper data cannot give a lead change inside a slot or inside a game. Sleeper
  saves final player totals only. The play by play in the cache can give it, with `time_of_day` per play. That
  needs a per-play fantasy score with the league scoring, which is a build, not a fetch.

### 4. Monday night

Yes. The data says it with no fetch. `raw/stats.json` `date` `"2026-11-02"` marks the Monday starters, and
`raw/matchups.json` `starters_points` gives their points.

- **Open before Monday:** matchups 1, 3, 4, and 5 had a Monday starter. Matchups 2 and 6 were final after
  Sunday night.
- **Open with a real chance:** only matchup 3. In matchups 4 and 5 the side behind had no Monday starter, or
  trailed by 59.72 with one Monday starter projected at 8.27. In matchup 1, Lil Fridge trailed by 34.95 with
  Jaxon Smith-Njigba projected at 21.56.
- **Flipped:** matchup 3 only. London Cooking led The Blue Tent by 3.67 after Sunday night. On Monday,
  Jadarian Price (`"13286"`, SEA) scored 4.7 for The Blue Tent. The Seattle Seahawks defense (`"SEA"`) scored
  -0.4 for London Cooking. The Blue Tent won 100.31 to 98.88. The sheet has `M3.result` and `M3.swing.13286`,
  but no fact that says the lead was London Cooking's before Monday.

### 5. The gaps and the one fetch for each

| Gap | The fetch or the read | Source | Reached now? | Cost |
| --- | --- | --- | --- | --- |
| The time of an in-game injury | No fetch. A read of `desc`, `qtr`, `time`, `time_of_day` for "was injured" plays. | cache `play_by_play_2026.csv.gz` | Yes. `nflverse.py` downloads it each build. | No HTTP call. Two more columns in a read of an 8.3 MB file. |
| The news of an injury, with a time | `GET https://api.sleeper.app/players/nfl/<player_id>/news` | Sleeper, unofficial | Yes. `provider.sleeper.fetch_news`, called by `sheet/assemble.py` for the Game Changer only. | 1 call per injured starter, 11 in week 8. Not saved to disk. |
| Sunday early, late, and night | No fetch. A read of `SlowSources.kickoffs` by team. | cache `games.csv` | Yes. `read_kickoffs` reads it. | No HTTP call. |
| The lead after each slot | No fetch. A sum of `starters_points` by slot. | `raw/matchups.json`, `raw/stats.json` | Yes. | No HTTP call. |
| The lead inside a game | No fetch. A per-play fantasy score. | cache `play_by_play_2026.csv.gz` | Yes, the file. No code scores a play. | A build. Out of scope for ticket 04. |

I made one live call of the news fetch for `"4881"`. It gave 5 items with `published` and
`metadata.description`. Sample: published 2026-11-02 15:42 UTC, "Lamar Jackson (thumb) is likely to miss the
remainder of the 2026 season after suffering an injury to his right thumb in Sunday's loss to the Buffalo
Bills". Prefer the play by play for the time, because it is already on disk and it gives the quarter.

### 6. Facts for ticket 04

The smallest set that lets a recap say the injury, the timing of the lead change, and the Monday night turn:

1. `injury_play`: the quarter, the clock, and the game of the play where a starter was hurt. Source: cache
   `play_by_play_2026.csv.gz`, columns `desc` (contains "was injured during the play"), `qtr`, `time`,
   `game_id`, `passer_player_id` or `rusher_player_id` or `receiver_player_id`. Sample: Lamar Jackson,
   `2026_08_BAL_BUF`, Q1 10:04.
2. `injury_snaps`: the snaps of the starter against his team's snaps. Source: `raw/stats.json`
   `<line>.stats.off_snp` and `.stats.tm_off_snp`. Sample: `"4881"` 1 of 51.
3. `injury_status`: the status and the body part now. Source: `raw/players.json` `<player_id>.injury_status`
   and `.injury_body_part`. Sample: `"Out"`, `"Thumb"`. The sheet has it as `M<n>.inj.<player_id>`.
4. `slot_of_starter`: the slot of each starter: Thursday, Sunday early, Sunday late, Sunday night, or Monday.
   Source: `raw/stats.json` `<line>.team`, with the cache `games.csv` `weekday` and `gametime`, as
   `SlowSources.kickoffs`.
5. `lead_by_slot`: each side's margin after each slot. Source: `raw/matchups.json` `starters` and
   `starters_points`, summed by `slot_of_starter`. Sample: matchup 3, London Cooking +3.67 after Sunday night.
6. `monday_turn`: the matchup whose leader after Sunday night lost, with the Monday starters and their points.
   Source: `lead_by_slot`, and `raw/stats.json` `date` `"2026-11-02"`. Sample: matchup 3, Jadarian Price 4.7,
   the Seattle Seahawks defense -0.4.

The saved data cannot give a lead change inside a game. It can give the lead change between slots, as in
the table of part 3. Only a per-play fantasy score over the play by play can give a lead change inside a game.

### Files read

In order, with one word on why:

1. `CLAUDE.md`: start.
2. `docs/agents/state.md`: hold.
3. `.scratch/week-8-fixes/issues/03-the-game-story-data-check.md`: task.
4. `.scratch/week-8-fixes/PRD.md`: scope.
5. `src/cornerstone/README.md`: map.
6. `src/cornerstone/provider/README.md`: fetches.
7. `src/cornerstone/sheet/README.md`: news.
8. `src/cornerstone/provider/base.py`, docstring: port.
9. `src/cornerstone/provider/sleeper.py`, docstring and constants: files.
10. `src/cornerstone/nflverse.py`, docstring and readers: sources.
11. `src/cornerstone/paths.py`: cache.
12. `data/2026/history/week-08/` 5 files and `data/2026/week-08/` 3 files and `raw/` 16 files, keys only: data.
13. `src/cornerstone/history.py`, `_save_injuries`: injuries.
14. `data/2026/history/week-06/injuries.json` and `week-07/injuries.json`: change.
15. `data/2026/week-07/raw/players.json`, one player: change.
16. cache `games.csv`, `injuries_2026.csv.gz`, `play_by_play_2026.csv.gz`, in the main checkout, read-only: timing.
17. `src/cornerstone/slow_sources.py`, `snapshot.py`, `sheet/assemble.py`, `sheet/awards.py`, by grep: users.
18. `GLOSSARY.md`, "Swing" and "Out": terms.
19. `src/cornerstone/nflverse_usage.py`, `PLAY_COLUMNS`: columns.
20. `src/cornerstone/pipeline.py`, `load_nflverse` and the save rule: extract.
21. `.gitignore`: cache.

Count: 20 code and doc files, 30 data files, and 1 live news call.

README verdict:

- The provider README line "It fetches no nflverse file and reads no trade value chart. `cornerstone/nflverse.py`
  and `cornerstone/chart.py` do." sent me to the right file for injuries, kickoffs, and the play by play.
- The sheet README line "`sheet/assemble.py` calls `provider.sleeper.fetch_news` by default" told me the news
  fetch is already reached.
- Missing: no README names the saved data layout: `data/<season>/week-NN/raw/`, `history/week-NN/injuries.json`,
  and the nflverse cache in `data/cache/nflverse/`. No README says the cache is absent in a fresh worktree, or
  that `raw/nflverse.json` is saved only when every source is complete.
- Wrong: `CLAUDE.md` Pipeline step 2 says "Cache the raw data under `data/cache/`". The raw data is in
  `data/<season>/week-NN/raw/`. `data/cache/` holds only the players file and the nflverse downloads.
- Unclear: `GLOSSARY.md` defines "Out" as a team that cannot make the playoffs. Sleeper `injury_status` also
  uses "Out". A recap with both needs a rule.
