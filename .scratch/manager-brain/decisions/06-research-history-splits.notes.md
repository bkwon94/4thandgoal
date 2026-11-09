# 06: Research notes on the past-season splits

Ticket: `decisions/06-research-history-splits.md`. Research date: 2026-11-09.
Paths with `packages/` are relative to the repo root. Cache paths are in the main checkout, because the worktree has no cache.

## Summary and recommendation

- **Source:** the nflverse weekly player file `stats_player_week_<season>.csv.gz`. The pipeline already downloads it for the current season, and it already maps its `gsis_id` to the Sleeper id. One download of about 1.2 MB gives one past season.
- **Seasons:** three, 2023 to 2025. The cost is about 3.7 MB in three downloads. Two seasons would drop the 2023 rows, and the 2023 rows show the Chase Brown pattern before his breakout.
- **Splits:** points per game in half PPR for weeks 1 to 8 and for weeks 9 to 17, with the count of games in each. Add a cold split, outdoor games at 40 F or below, with the game count. The schedules file already in the cache has the kickoff temperature.
- **Cache path:** `data/nfl/cache/nflverse/stats_player_week_<season>.csv.gz`, the same name that `cache_path` gives now. A past season never changes, so it needs a max age with no limit, not the one-day max age. The folder is in `.gitignore` and on the Fly volume.
- **Fallback and cross-check:** the undocumented Sleeper endpoint `https://api.sleeper.app/stats/nfl/player/<id>?season_type=regular&season=<season>&grouping=week`. It gave the same numbers as nflverse for all six sample rows below.

## 1. Sleeper weekly stats of past seasons

- The official docs at https://docs.sleeper.com list no stats endpoint. The table of contents has only users, leagues, rosters, matchups, transactions, drafts, players, trending players, and the NFL state. Source: GET of https://docs.sleeper.com on 2026-11-09, the anchor list of the page.
- The docs give one limit: "stay under 1000 API calls per minute, otherwise, you risk being IP-blocked". Source: the same page.
- The repo already calls the undocumented weekly endpoint `https://api.sleeper.app/stats/nfl/<season>/<week>`, with `season_type=regular` and one `position[]` per position. Source: `packages/league/python/src/league/provider/sleeper.py:33-34` for the base URLs, `:63-65` for the params, and `:216-217`, `:272`, `:287-288` for the calls. Line 80 of that file says why a failure must not stop the report: "Unofficial endpoints change without notice".
- The weekly endpoint answers for past seasons. Week 1 gave HTTP 200 for 2009, 2012, 2015, 2017, 2020, 2023, 2024, and 2025. The row counts for RB only in week 1 grow with time: 38 in 2009, 98 in 2012, 164 in 2015. So the old seasons are thin, and 2017 onward looks full. Source: GET calls on 2026-11-09, scratch files in the scratchpad `history/` folder.
- Each row holds `player_id`, `team`, `opponent`, `game_id`, `date`, `week`, `season`, and `stats` with `pts_std`, `pts_half_ppr`, `pts_ppr`, `gp`, `off_snp`, `rush_att`, `rec_tgt`, and more. Source: week 1 of 2024, the row of player `3198`.
- A per-player endpoint also works: `https://api.sleeper.app/stats/nfl/player/<id>?season_type=regular&season=<season>&grouping=week`. It gives one object keyed by week, about 16 KB per season. The `api.sleeper.com` host gives the same body. The repo does not call this endpoint. Source: GET calls on 2026-11-09, and a grep of `packages` and `apps` for `stats/nfl/player`, which found nothing.

## 2. Past seasons in the slow sources of the pipeline

- The weekly player file of nflverse is `STATS_PLAYER_URL`, with a `{season}` field. Source: `packages/league/python/src/league/nflverse.py:33-34`.
- The fetch downloads it for the build season only. Source: `nflverse.py:317-320` and `:342-344`. The slow-source loader reads it for the WOPR only. Source: `packages/league/python/src/league/slow_sources.py:107-110`.
- The cache holds only `stats_player_week_2026.csv.gz` now, so it has no past season. Source: listing of `data/nfl/cache/nflverse/` on 2026-11-09.
- The release has past seasons. The files of 2023, 2024, and 2025 gave HTTP 200 at 1,237,909, 1,244,175, and 1,262,421 bytes. Source: GET calls on 2026-11-09.
- The columns include `player_id` (the gsis id), `season`, `week`, `season_type`, `game_id`, `team`, `opponent_team`, `fantasy_points`, and `fantasy_points_ppr`. Half PPR is the mean of the two. Source: the header of `stats_player_week_2026.csv.gz`.
- The id map is the dynastyprocess file `db_playerids.csv`, with columns `sleeper_id` and `gsis_id`. Source: `nflverse.py:35` for the URL, and `nflverse.py:291-293` for `read_id_map`.
- The pipeline prefers the `gsis_id` of the Sleeper players file, and uses the map when that is empty. Source: `nflverse.py:296-301`. Chase Brown needs the map: his entry in `players.json` has no `gsis_id`, and `db_playerids.csv:1120` maps `9224` to `00-0038597`.
- The current reader `read_player_weeks` reads targets, shares, and WOPR, not points. Source: `packages/league/python/src/league/nflverse_players.py:31-51`. A history reader needs the two points columns too.
- The schedules file `games.csv` holds every season from 1999 to 2026 in one file, 7,548 games. It has the columns `roof`, `temp`, and `wind`. Source: `nflverse.py:29-30` and the file in `data/nfl/cache/nflverse/games.csv`.

## 3. The cost

| Source | Calls per season | Size per season | Notes |
| --- | --- | --- | --- |
| nflverse `stats_player_week_<season>.csv.gz` | 1 download | about 1.2 MB gzip | All players. The current code path and id map fit. |
| Sleeper weekly endpoint | 18 calls, one per week | about 0.75 MB JSON per week, about 13 MB per season | All players of the six positions. |
| Sleeper per-player endpoint | 1 call per player | about 16 KB | About 300 rostered players in a league means about 300 calls per season. |

Sources: the byte counts of the GET calls on 2026-11-09.

The cache rules now:

- Each download goes to `cache_path(cache_dir, url_template, season)`, the last part of the URL in one folder. Source: `nflverse.py:304-306`.
- `download` keeps a file for one day, then fetches it again, and falls back to a stale file on a failure. Source: `nflverse.py:37-38` and `:55-70`.
- The folder is `data/nfl/cache/nflverse`. Source: `packages/league/python/src/league/paths.py:96-98`.
- `.gitignore:10` ignores `data/nfl/cache/`, with the comment "Each run fills them again".
- The API keeps the cache on the Fly volume. Source: `apps/api/fly.toml:41-44`, "One volume holds the tracked data seed, the nflverse cache, the charts, and the result cache".

A past-season file fits in the same folder under the same name rule. Pass a max age with no limit to `download`, because a past season does not change. The slow-source loader reads from the cache with no network call (`slow_sources.py:75`), so the fetch step must download the past seasons, not the loader.

## 4. The splits, with a sample

Half PPR points per game, with the games played in brackets. Weeks 9 to 17 exclude week 18. "Cold" is an outdoor or open-roof game with a kickoff temperature of 40 F or below in `games.csv`. "Other" is every other outdoor game with a temperature. Dome games are in neither.

| Player | Season | Team | Weeks 1 to 8 | Weeks 9 to 17 | Cold | Other outdoor |
| --- | --- | --- | --- | --- | --- | --- |
| Derrick Henry | 2023 | TEN | 13.7 (7) | 12.8 (9) | 17.7 (1) | 14.1 (11) |
| Derrick Henry | 2024 | BAL | 21.4 (8) | 15.8 (8) | 18.6 (3) | 18.5 (11) |
| Derrick Henry | 2025 | BAL | 12.8 (7) | 18.8 (9) | 21.6 (5) | 14.0 (11) |
| Chase Brown | 2023 | CIN | 0.6 (5) | 6.3 (6) | 9.2 (3) | 2.6 (7) |
| Chase Brown | 2024 | CIN | 10.2 (8) | 18.2 (8) | 14.9 (2) | 13.3 (12) |
| Chase Brown | 2025 | CIN | 10.4 (8) | 18.5 (8) | 15.3 (4) | 15.2 (12) |

Sources: the Sleeper per-player endpoint for 2023 to 2025, the nflverse files of 2023 to 2025, and `games.csv`. The script is `history/splits.py` in the scratchpad. The Sleeper `pts_half_ppr` and the nflverse half PPR give the same value in every half split.

What the sample says:

- The playbook claim "Chase Brown in the second half" holds in all three seasons.
- The claim "Henry in the second half" holds in 2025 only. In 2024 he was better in weeks 1 to 8, and 2023 is about even. A check on the sheet would block "Henry always finishes strong" as a number claim.
- The cold games of Henry are 1, 3, and 5 games. Show the game count with each cold split, so the judge does not lean on one game.

Weather:

- The Sleeper stats rows hold no weather field. Source: the keys of the 2024 week 1 row.
- The nflverse weekly player file holds no weather column. Source: its header.
- The nflverse schedules file `games.csv` holds `temp`, `wind`, and `roof` for each game, and joins on `game_id`. So a cold split is possible from a file the pipeline already caches.
- Coverage of `temp` for outdoor regular-season games that were played: 41 games with no temp in 2023, 5 in 2024, and 4 in 2025. Most of the 2023 gaps are in weeks 1 and 2, 24 of 41. Source: a count over `games.csv` on 2026-11-09. A cold split cares about late games, and those have the temperature.

## 5. How a player maps across seasons and teams

- The Sleeper player id stays the same across seasons and teams. Henry is `3198` in every season. The per-player endpoint gives `team` TEN for 2023 and BAL for 2024 and 2025 under that one id. Source: the files `sp_3198_<season>.json` in the scratchpad.
- The gsis id of nflverse also stays the same: Henry is `00-0032764` in each of the three files, and the splits above match on it.
- The join is Sleeper id to gsis id, by `gsis_id` of the Sleeper players file first, then `db_playerids.csv`. Source: `nflverse.py:296-301`. The pipeline builds the reverse map `sleeper_of_gsis` from it. Source: `slow_sources.py:98-99`.
- The team of a past game comes from the row, `team` in nflverse and `team` in Sleeper, not from the current roster. So a split can say "with TEN" for 2023.
- One gap: a player with no gsis id in either place drops out of the nflverse rows. Source: `nflverse_players.py:35-36`. That player has no split, and the judge states his history with no number.

## 6. Recommendation

1. Use the nflverse weekly player file as the source. It is a documented, versioned release. The pipeline already downloads it, maps its ids, and caches it. Its `game_id` joins `games.csv` for the cold split.
2. Use three seasons, 2023 to 2025. The cost is three downloads, about 3.7 MB, once per season. Old seasons never change, so the cost is paid once.
3. Hold these splits on the sheet, for each player in the trade, per season: the team, half PPR points per game in weeks 1 to 8 and in weeks 9 to 17 with the game counts, and the cold points per game with the game count. Use the points key of the league, so a PPR client reads `fantasy_points_ppr`.
4. Cache the files at `data/nfl/cache/nflverse/stats_player_week_<season>.csv.gz`, under the current `cache_path` rule, with a max age with no limit for a past season.
5. Keep the Sleeper per-player endpoint as a cross-check only. It is undocumented, and the repo treats such endpoints as able to change without notice.
