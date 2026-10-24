# The nflverse inventory

Date: 2026-10-24. All web claims were read on 2026-10-24. The release facts come from the GitHub
API for `nflverse/nflverse-data` (`gh api repos/nflverse/nflverse-data/releases`) and from the
CSV headers of the live files.

## The short answer

No, we do not get the most from nflverse. We download 7 files and read about 40 columns. Three
gains cost almost nothing, because the data is already in our cache: the betting lines in
`games.csv`, and `pass_oe` and `epa` in the play by play. One file, `stats_player`, already holds
target share, air yards share, and WOPR. Routes run do not exist in nflverse during the season.

## Part 1: what we use today

Every file goes through `nflverse.download` with a one-day cache in `data/cache/nflverse/`.

| File | URL template | Columns we read | Reader | Feature |
| --- | --- | --- | --- | --- |
| Play by play | `releases/download/pbp/play_by_play_{season}.csv.gz` | `week`, `season_type`, `play_type`, `game_id`, `play_id`, `home_team`, `away_team`, `receiver_player_id`, `air_yards`, `yardline_100`, `posteam`, `pass`, `rush`, `rusher_player_id`, `success`, `down`, `score_differential`, `qtr`, `game_seconds_remaining` | `read_drops`, `read_plays`, `read_usage`, `read_environment` | Drop lines, usage trend, environment |
| FTN charting | `releases/download/ftn_charting/ftn_charting_{season}.csv` | `week`, `nflverse_game_id`, `nflverse_play_id`, `is_drop` | `read_drops` | Drop lines |
| Injuries | `releases/download/injuries/injuries_{season}.csv.gz` | `season_type`, `week`, `gsis_id`, `report_status` | `read_injuries` | Injury adjuster, story fact, stashes |
| Schedules | `releases/download/schedules/games.csv` | `season`, `game_type`, `week`, `away_team`, `home_team` | `read_schedules` | Bye weeks, playoff opponents in the schedule adjuster |
| Depth charts | `releases/download/depth_charts/depth_charts_{season}.csv.gz` | `dt`, `team`, `pos_abb`, `pos_rank`, `gsis_id` | `read_depth_charts` | Handcuff, story fact, sneaky |
| Snap counts | `releases/download/snap_counts/snap_counts_{season}.csv` | `game_type`, `week`, `pfr_player_id`, `offense_snaps`, `offense_pct`, `team` | `read_snaps` | Snap share, drop candidates |
| ffverse id map | `github.com/dynastyprocess/data/raw/master/files/db_playerids.csv` | `sleeper_id`, `gsis_id`, `pfr_id` | `read_id_map`, `read_pfr_map` | Joins Sleeper ids to nflverse ids |

`points_allowed.py` reads the Sleeper stat lines in the history, not nflverse. The PRD asks for
"routes where the charting has them". The FTN file has no route column, so the code reads none.

## Part 2: what nflverse offers

Source: the release list, and the schedule page
`https://nflreadr.nflverse.com/articles/nflverse_data_schedule.html`. "Updated" is the asset
time on 2026-10-24.

| Release tag | 2026 file | Columns that matter | Update cadence | Updated |
| --- | --- | --- | --- | --- |
| `pbp` | `play_by_play_2026.csv.gz`, 372 columns | `xpass`, `pass_oe`, `epa`, `cpoe`, `qb_dropback`, `air_yards`, `yards_after_catch`, `xyac_mean_yardage`, `wp`, `shotgun` | Nightly after game days; stat fixes Wed to Thu night | 10-24 09:04Z |
| `stats_player` | `stats_player_week_2026.csv.gz`, also `reg` and `regpost` | `targets`, `target_share`, `air_yards_share`, `wopr`, `receiving_air_yards`, `racr`, `carries`, `fantasy_points_ppr`, `passing_epa` | Same as pbp | 10-24 09:05Z |
| `stats_team` | `stats_team_week_2026.csv.gz` | Team sums of the same columns | Same as pbp | 10-24 09:05Z |
| `player_stats` | none for 2026 | none | Deprecated: "DEPRECATED 2025-08-01: USE `stats_player` OR `stats_team` INSTEAD" | 2025-05-07 |
| `ftn_charting` | `ftn_charting_2026.csv` | `is_catchable_ball`, `is_contested_ball`, `is_screen_pass`, `is_play_action`, `read_thrown`, `is_created_reception`, `n_defense_box` | 0, 6, 12, 18 UTC daily | 10-22 03:12Z |
| `snap_counts` | `snap_counts_2026.csv` | `offense_pct`, `st_pct` | 0, 6, 12, 18 UTC daily | 10-23 11:32Z |
| `injuries` | `injuries_2026.csv.gz` | `practice_status`, `report_primary_injury` | 7 AM UTC daily | 10-24 11:57Z |
| `depth_charts` | `depth_charts_2026.csv.gz` | Same as today; time stamps, not weeks, from 2025 on | 7 AM UTC daily | 10-24 11:58Z |
| `rosters` | `roster_2026.csv` | `status`, `sleeper_id` | 7 AM UTC daily | 10-24 06:04Z |
| `weekly_rosters` | `roster_weekly_2026.csv` | `week`, `status`, `status_description_abbr`, `sleeper_id`, `gsis_id`, `pfr_id` | Not stated | 10-24 06:04Z |
| `schedules` | `games.csv` | `spread_line`, `total_line`, `away_moneyline`, `home_moneyline`, `away_rest`, `home_rest`, `roof`, `wind`, `temp` | Every 5 minutes in season | 10-24 06:36Z |
| `players` | `players.csv` | `gsis_id`, `pfr_id`, `espn_id`, `status`, `draft_round` | Not stated | 10-23 14:17Z |
| `nextgen_stats` | `ngs_receiving.csv.gz`, `ngs_rushing.csv.gz`, `ngs_passing.csv.gz`, one file for all seasons | Receiving: `avg_separation`, `avg_cushion`, `avg_intended_air_yards`, `percent_share_of_intended_air_yards`, `avg_yac_above_expectation`, `player_gsis_id` | Nightly, 3 to 5 AM ET | 10-24 11:45Z, holds 2026 week 7 |
| `pfr_advstats` | `advstats_week_{pass,rush,rec,def}_2026.csv`, `advstats_season_*.csv` | Week rush: `rushing_yards_after_contact_avg`, `rushing_broken_tackles`. Week rec: `receiving_drop`, `receiving_rat`. Season rec: `adot`, `ybc`, `yac`, `brk_tkl` | 0, 6, 12, 18 UTC daily | 10-22 to 10-23 |
| `espn_data` | `qbr_week_level.csv`, `qbr_season_level.csv` | `qbr_total`, `pts_added`, `epa_total` | Not stated | 10-23 14:43Z |
| `pbp_participation` | none for 2026; last is `pbp_participation_2025.csv` | `offense_players`, `route`, `was_pressure`, `defense_coverage_type` | No updates in season | 2026-02-10 |
| `contracts` | `historical_contracts.csv.gz` | `apy`, `years` | Not stated | CSV 2022-05-29, `.qs` 2026-03-19 |
| `officials` | `officials.csv` | crew by game | Not stated | 2026-09-02 |
| `draft_picks` | `draft_picks.csv` | round, pick, team | Not stated | 10-21 |
| `combine` | `combine.csv` | forty, vertical | Not stated | 2026-03-12 |
| `trades` | `trades.csv` | NFL trades | Not stated | 2026-05-19 |
| `teams` | `teams_colors_logos.csv` | colors, logo URLs | Not stated | 2026-03-27 |
| `players_components`, `misc`, `test` | build parts and one-off files | none of use | Not maintained | varies |

A sibling repo, `ffverse/ffopportunity`, tag `latest-data`, holds `ep_weekly_2026.csv`. It gives
expected fantasy points per player per week: `total_fantasy_points_exp`, `rec_fantasy_points_exp`,
`rush_fantasy_points_exp`, and the `*_diff` columns. Updated 2026-10-23 10:31Z.

### Participation and routes

Participation is not live for 2026. The schedule page says the data "does not update during the
season", and FTN sends the season only after the Super Bowl. The 2025 file holds every week
through week 22. Its `route` column is the route of the primary receiver only, not every route.
FTN charting and Next Gen Stats have no route column either. So nflverse gives no routes run in
season. Use snap share on pass plays as the proxy. The waiver engine already does close to that.

## Part 3: the map to features

| File | Columns | Ready by Tuesday | Feature it would improve or create |
| --- | --- | --- | --- |
| `schedules` lines, already cached | `spread_line`, `total_line` | Yes, next week only | Implied team total in the environment score and fact |
| `stats_player` week | `target_share`, `air_yards_share`, `wopr`, `receiving_air_yards` | Yes, Monday night games by Tuesday morning | Opportunity score in the usage trend; sneaky WR signal |
| `pbp` extra columns, already cached | `pass_oe`, `epa`, `xpass` | Yes | Pass rate over expected and EPA per play in the environment |
| `ffopportunity` `ep_weekly` | `total_fantasy_points_exp`, `total_fantasy_points_diff` | Usually; updated 10-23 for week 6 | "Due for points" fact for waivers and the trade finder |
| `nextgen_stats` receiving | `avg_separation`, `percent_share_of_intended_air_yards` | Yes, 3 to 5 AM ET | Sneaky WR fact |
| `pfr_advstats` week rush | `rushing_yards_after_contact_avg`, `rushing_broken_tackles` | Yes, mostly | RB efficiency fact for sneaky and drops |
| `stats_player` week | all box score columns, `fantasy_points_ppr` | Yes | One-file weekly box score for position leaders and awards |
| `weekly_rosters` | `status`, `sleeper_id` | Yes | A second id map, from nflverse itself; NFL practice squad status |
| `injuries` extra columns | `practice_status`, `report_primary_injury` | Yes | Richer story fact: "DNP Wednesday, hamstring" |
| `espn_data` QBR | `qbr_total` | Yes | QB quality term for a WR's environment |
| `ftn_charting` extra columns | `is_catchable_ball`, `is_contested_ball` | Yes | Catchable target rate for a WR |
| `pbp_participation` | `offense_players`, `route` | No, offseason only | Nothing in season |
| `draft_picks`, `combine` | round, forty | Static | Rookie context in a story fact, low value |
| `contracts`, `trades` | apy, NFL trades | Static | Nothing for a redraft league |
| `officials` | crew | Not stated | Nothing. Referee crews do not move fantasy points enough to show |
| `teams` | colors, logos | Static | Site look only |

### Top five, ranked

**1. Betting lines from `games.csv`.** The manager sees "Vegas gives NYJ 27 points this week" in
the environment fact of each waiver player. The matchups chapter can show the same total for the
NFL games of each starter. The engine reads `spread_line` and `total_line` and computes the
implied team total, `(total + spread) / 2` for the home team. That rank joins plays per game in
the environment score. The cost is about one hour. The file is already in the cache, and
`read_schedules` already walks every row. The limit: the lines exist only through next week. On
10-24 the cache had lines for weeks 1 to 8 and none for week 9 on.

**2. Opportunity shares from `stats_player`.** The manager sees "18% of targets and 31% of air
yards" on a sneaky WR. A deep target is worth more than a screen, and air yards show that. The
engine adds `air_yards_share` and `wopr` to the usage trend and scores the change across
`USAGE_WEEKS`. Sneaky gains a WOPR rise with a low projection. The cost is about half a day. The
file keys players by gsis id, so the existing `sleeper_of_gsis` map joins it. One new download,
about 1 MB gzipped.

**3. Pass rate over expected and EPA from the play by play.** The manager sees "MIA passes 8% more
than expected" on the environment fact. Neutral pass rate is a rough proxy. `pass_oe` is the
direct measure, because it controls for down, distance, and score. The engine adds `pass_oe` and
`epa` to `PLAY_COLUMNS` and averages them per team per week in `read_environment`. The power
rankings can use offense EPA per play as a fact. The cost is about two hours, with no new
download. The plays already sit in memory.

**4. Expected fantasy points from `ffopportunity`.** The manager sees "Expected 14.2, scored 6.1:
the volume is real, the touchdowns will come." This fits sneaky adds, drops, and the trade finder
as a buy-low or sell-high signal. The engine reads `total_fantasy_points_exp` and
`total_fantasy_points_diff` per player per week. The model is full PPR, so a half-PPR league needs
a rescale from the component columns. The cost is about a day, because of the rescale and a new
host to cache. The file arrived Friday for week 6, so a Tuesday build may lack the latest week.
Treat a missing week as a missing source.

**5. Separation and air yards share from Next Gen Stats.** The manager sees "He gets 3.4 yards of
separation, top 10 among WRs" in a sneaky WR row. The engine reads `avg_separation` and
`percent_share_of_intended_air_yards` from `ngs_receiving.csv.gz` and ranks them by position. The
cost is about half a day. The file joins on `player_gsis_id`. Two limits: NGS lists only players
with enough targets, so a deep waiver WR may be absent. Week 0 rows are season totals and must be
filtered. Air yards share overlaps item 2, so build item 2 first.

Next in line: PFR yards after contact for RBs, and practice status in the story fact.

## Does `stats_player` duplicate our usage sums?

Partly yes. The nflreadr dictionary (`data-raw/dictionary_player_stats.json`, read via the GitHub
API on 2026-10-24) defines:

- `target_share`: "Player's share of team receiving targets in this game".
- `air_yards_share`: "Player's share of the team's air yards in this game".
- `wopr`: "1.5 x target_share + 0.7 x air_yards_share".

So `read_usage` repeats work for targets and target share. It does not repeat the rest.
`stats_player` has `carries` but no carry share, no red zone touches, and no snaps. The team
environment and the neutral pass rate are not in `stats_team` either. Keep `read_plays` for
those. A swap of the target count to `stats_player` removes one rule of our own about which plays
count. Our count keeps `play_type` pass or run. The count in `nflfastR::calculate_stats` may treat
a play with a penalty in a different way. A test must compare the two counts on real weeks
before the swap.

## Not confirmed

- The update cadence of `weekly_rosters`, `players`, `espn_data`, `contracts`, `officials`,
  `draft_picks`, `combine`, `trades`, and `teams`. The schedule page gives none.
- The play filter of `nflfastR::calculate_stats` for targets, so the exact gap to our count.
- The weekday that `ffopportunity` updates. One asset time, Friday 10-23, is all I saw.
- The column lists of the PBP and player stats dictionary pages. Those pages render with
  JavaScript and returned no table. I used the live CSV headers and the dictionary files in
  the `nflverse/nflreadr` repo instead.
- Whether the betting lines in `games.csv` change through the week, or freeze at one source.
