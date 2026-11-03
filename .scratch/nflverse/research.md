# nflverse and ffverse: update times, targets, and null columns

Date: 2026-10-24. All sources were read on 2026-10-24. This file adds to
`.scratch/waiver/pipeline/nflverse-inventory.md` and corrects two items in it.

Time zones: in October, ET is EDT, which is UTC minus 4. So 04:30Z is 00:30 ET, and 12:00Z is
08:00 ET. The build runs Tuesday at 08:00 ET, which is 12:00Z.

## The short answer

1. `stats_player` and the play by play are safe for a Tuesday 08:00 ET build. In each of the last
   four Tuesdays, both files held the Monday night game by about 00:35 ET.
2. `ffopportunity` is not safe at 08:00 ET. Its Tuesday upload landed between 06:26 and 08:57 ET.
   In two of four weeks it landed after 08:00 ET. Before that upload, the file lacks the Monday
   night game.
3. A `stats_player` target is a play with NFL stat id 115. On real 2026 data, that equals every
   play with a `receiver_player_id`, minus two-point tries. A play that a penalty wipes out has no
   target. A play with a penalty that stands keeps its target.
4. For half PPR, subtract `0.5 * receptions_exp` from `total_fantasy_points_exp`.
5. `epa` is never null on a pass or run play. `pass_oe` is null on two-point tries, and on every
   play that is not a pass, a run, or a penalty play with a snap.

## Corrections to the inventory

1. The inventory gives the tag as `latest-data`, and the task gives `latest_data`. The real tag is
   `latest-data`. Source: `https://api.github.com/repos/ffverse/ffopportunity/releases`.
2. The inventory says the `ffopportunity` file "arrived Friday for week 6". That is wrong. Every
   run of the job rebuilds the whole season and overwrites every asset. The asset time shows only
   the last run. On 2026-10-24 the file held all 14 games of week 6, Monday night too, and the
   Thursday game of week 7. Sources: the script at
   `https://github.com/ffverse/ffopportunity/blob/main/update/ep_update.R`, and the game count per
   week in `ep_weekly_2026.csv`.

## Question 1: ffopportunity

### When the weekly files update

The workflow file sets five cron times, all in UTC. Source:
`https://github.com/ffverse/ffopportunity/blob/main/.github/workflows/ep-update-data.yaml`.

```yaml
# TNF 5:45 AM UTC / 12:45 AM ET
- cron:  '45 5 * 1,2,9-12 5'
# Early window: 10:15 PM UTC / 5:15 PM ET
- cron:  '15 22 * 1,2,9-12 0'
# Late window: 0:20 UTC / 8:20 ET
- cron:  '20 0 * 1,2,9-12 1'
# SNF/MNF: 5:45 UTC / 12:45 ET
- cron:  '45 5 * 1,2,9-12 1'
- cron:  '45 5 * 1,2,9-12 2'
```

So the job aims at Friday, Sunday night, Monday, and Tuesday. The Tuesday cron is 05:45Z, or
01:45 ET. GitHub starts these scheduled runs hours late. The run list shows the real times.
Source: `https://api.github.com/repos/ffverse/ffopportunity/actions/workflows/ep-update-data.yaml/runs`.

The asset time cannot show past weeks, because each run overwrites it. So I read the upload line
in the log of each Tuesday run. Source: the job logs under
`https://github.com/ffverse/ffopportunity/actions/workflows/ep-update-data.yaml`.

| Tuesday | Run start | Upload done, UTC | Upload done, ET | Ready at 08:00 ET |
| --- | --- | --- | --- | --- |
| 2026-09-29 | 11:33Z | 11:35:15Z | 07:35 | Yes |
| 2026-10-06 | 12:12Z | 12:14:37Z | 08:14 | No |
| 2026-10-13 | 12:56Z | 12:57:36Z | 08:57 | No |
| 2026-10-20 | 10:24Z | 10:26:15Z | 06:26 | Yes |

The Friday runs of the same weeks landed between 10:02Z and 11:20Z. The latest asset time is
Friday 2026-10-23 10:31Z, from the Thursday night game run. Source:
`https://api.github.com/repos/ffverse/ffopportunity/releases/tags/latest-data`.

The job reads the nflverse play by play through `nflreadr::load_pbp(season)`. So it can never be
newer than the play by play. Source:
`https://github.com/ffverse/ffopportunity/blob/main/R/ep_build.R`.

The weekday answer: the files update on Friday, Sunday night, Monday, and Tuesday. The Tuesday
update is the one with Monday night. It lands between about 06:30 and 09:00 ET.

### The file

`ep_weekly_2026.csv` holds one row per player per game. It also comes as `.parquet` and `.rds`.
The URL is
`https://github.com/ffverse/ffopportunity/releases/download/latest-data/ep_weekly_2026.csv`.
It is about 1.8 MB. Key columns: `season`, `posteam`, `week`, `game_id`, `player_id`,
`full_name`, `position`. The `player_id` is the gsis id. Source: the CSV header of the live file.

On 2026-10-24 the file held weeks 1 to 7: 16, 16, 16, 16, 15, 14, and 1 games.

### The scoring formula

The formula sits in `R/ep_summarize.R`. Source:
`https://github.com/ffverse/ffopportunity/blob/main/R/ep_summarize.R`.

| Part | Formula for the `_exp` points |
| --- | --- |
| Receiving | `0.1 * yards_gained_exp + 1 * complete_pass_exp + 6 * touchdown_exp + 2 * two_point_conv_exp` |
| Rushing | `0.1 * rush_yards_exp + 6 * rush_touchdown_exp`, or `2 * two_point_conv_exp` on a two-point try |
| Passing | `0.04 * yards_gained_exp - 2 * interception_exp + 4 * touchdown_exp + 2 * two_point_conv_exp` |

The receiving part gives 1 point per expected catch. That is full PPR. Fumbles are not in any
`_exp` part.

### The columns for a half-PPR rescale

All names are exact, from the header of the live file.

| Concept | Column |
| --- | --- |
| Total expected points, full PPR | `total_fantasy_points_exp` |
| Expected receptions | `receptions_exp` |
| Expected receiving yards | `rec_yards_gained_exp` |
| Expected receiving touchdowns | `rec_touchdown_exp` |
| Expected receiving two-point | `rec_two_point_conv_exp` |
| Receiving points, full PPR | `rec_fantasy_points_exp` |
| Expected rushing yards | `rush_yards_gained_exp` |
| Expected rushing touchdowns | `rush_touchdown_exp` |
| Expected rushing two-point | `rush_two_point_conv_exp` |
| Rushing points | `rush_fantasy_points_exp` |
| Expected passing yards | `pass_yards_gained_exp` |
| Expected passing touchdowns | `pass_touchdown_exp` |
| Expected interceptions | `pass_interception_exp` |
| Expected passing two-point | `pass_two_point_conv_exp` |
| Passing points | `pass_fantasy_points_exp` |
| Expected total touchdowns | `total_touchdown_exp` |
| Actual points, full PPR | `total_fantasy_points` |
| Actual receptions | `receptions` |

`total_fantasy_points_exp` equals `rec_fantasy_points_exp + rush_fantasy_points_exp +
pass_fantasy_points_exp`. The code says so, and all 1,991 rows match to 0.00.

The half-PPR rescale:

```text
half_ppr_exp    = total_fantasy_points_exp - 0.5 * receptions_exp
half_ppr_actual = total_fantasy_points     - 0.5 * receptions
```

I checked the receiving identity on all 1,991 rows. The largest gap is 0.037 points. The cause is
the round of each column to two places. The rushing identity has gaps up to 0.155 points. The
code adds `0.1 * rush_yards_exp` on a two-point try, but it sets the yards column to 0 on that
try. The half-PPR rescale touches only `receptions_exp`, so neither gap matters to it.

## Question 2: stats_player

### The file

The weekly file is `stats_player_week_2026.csv.gz`. It also comes as `.csv`, `.parquet`, and
`.rds`. The URL is
`https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_2026.csv.gz`.
It is about 427 KB. It has one row per player per week, with `week`, `season_type`, `game_id`,
and `team`. Source: `https://api.github.com/repos/nflverse/nflverse-data/releases/tags/stats_player`
and the CSV header.

`stats_player_reg_2026` and `stats_player_regpost_2026` are season totals. They have no `week`
column.

The job that builds the file calls `nflfastR::calculate_stats(seasons = season, summary_level =
"week", stat_type = "player")`. Source:
`https://github.com/nflverse/nflverse-pbp/blob/master/R/update_stats.R`.

### Which plays count as a target

Source: `https://github.com/nflverse/nflfastR/blob/master/R/calculate_stats.R`, last changed
2026-08-06, commit `4fc75e8`.

1. `calculate_stats` does not count targets from the play by play. It counts the NFL stat ids in
   the `play_stats_{season}.rds` file of the `nflverse-pbp` repo.
2. `targets = sum(stat_id == 115)`. Stat id 115 is the NFL "pass target" stat.
3. The team total is `team_targets = sum(stat_id == 115)` per team per week.
4. `target_share = targets / team_targets`.
5. `receiving_air_yards` sums, over each target, the air yards of that play. The air yards come
   from stat ids 111 and 112, which belong to the passer.
6. `team_air_yards` sums stat ids 111 and 112 per team per week.
7. `air_yards_share = receiving_air_yards / team_air_yards`.
8. `wopr = 1.5 * target_share + 0.7 * air_yards_share`.

The play by play gets `receiver_player_id` from the same stat id 115. Source:
`https://github.com/nflverse/nflfastR/blob/master/R/helper_tidy_play_stats.R`, line 1292.

### What that means on real data

The source does not name penalty plays. So I tested the rule on the 2026 data. I read the
`targets` column of `stats_player_week_2026.csv.gz`. I read four columns of
`play_by_play_2026.parquet` with HTTP range requests, about 220 KB.

| Play rule on the play by play | Team-weeks that match `targets` | Plays |
| --- | --- | --- |
| Every play with `receiver_player_id` | 158 of 188 | 6,052 |
| The same, minus `two_point_attempt == 1` | 188 of 188 | 6,018 |
| `play_type` pass or run, with `receiver_player_id` | 158 of 188 | 6,052 |

The rule that matches every team-week:

```text
target = receiver_player_id is not null AND two_point_attempt != 1
```

Penalty plays:

1. A play that a penalty wipes out has `play_type` `no_play`. None of the 1,761 `no_play` rows
   has a `receiver_player_id`. So it has no target.
2. A play with a penalty that stands keeps `play_type` `pass`. 98 such plays have `penalty == 1`,
   and 83 of them have a receiver. They count as targets.
3. A two-point try with a receiver does not count. There are 34 in 2026.

Our own count keeps `play_type` pass or run with a receiver. It counts the 34 two-point tries,
so it is 34 targets too high. Add `two_point_attempt != 1` to match nflverse exactly.

### When the file updates after Monday night

The same workflow builds the play by play and `stats_player`. The `stats` job waits for the
`pbp` job. Source: `https://github.com/nflverse/nflverse-pbp/blob/master/.github/workflows/update_data.yaml`.

```yaml
# Every day at 9:00 UTC/5:00 ET
- cron:  '3 9 * 1,2,9-12 *'
# TNF 5:30 AM UTC / 12:30 AM ET
- cron:  '33 5 * 1,2,9-12 5'
# Early window: 10:00 PM UTC / 5:00 PM ET
- cron:  '3 22 * 1,2,9-12 0'
# Late window: 0:00 UTC / 8:00 ET
- cron:  '7 0 * 1,2,9-12 1'
# SNF/MNF: 5:30 UTC / 12:30 ET
- cron:  '33 5 * 1,2,9-12 1'
- cron:  '33 5 * 1,2,9-12 2'
```

`nflverse-data/workflows.md` lists the same times with minute 0 or 30. Source:
`https://github.com/nflverse/nflverse-data/blob/master/workflows.md`.

The `nflverse-data` repo itself has no update workflow for these files. Its workflows are
`heartbeat.yml`, `run_archive.yaml`, `run_s3_archive.yaml`, and `test.yaml`.

The scheduled runs start hours late. But a second trigger runs on time. Each day at 09:00Z, and
at 04:30Z on Monday, Tuesday, and Friday, a `workflow_dispatch` run starts within 5 seconds. The
user `guga31bb` triggers it. Source:
`https://api.github.com/repos/nflverse/nflverse-pbp/actions/workflows/update_data.yaml/runs`.

I read the job logs of the 04:30Z Tuesday runs. The "Start download of N games" line gives the
game count. The game count per week comes from `games.csv`.

| Tuesday | Games in pbp | Games through that week | pbp upload | `stats_player` upload | ET |
| --- | --- | --- | --- | --- | --- |
| 2026-09-29 | 48 | 48, weeks 1 to 3 | 04:33:05Z | 04:34:43Z | 00:35 |
| 2026-10-06 | 64 | 64, weeks 1 to 4 | 04:33:13Z | 04:34:48Z | 00:35 |
| 2026-10-13 | 79 | 79, weeks 1 to 5 | 04:33:39Z | 04:35:08Z | 00:35 |
| 2026-10-20 | 93 | 93, weeks 1 to 6 | 04:33:26Z | 04:35:00Z | 00:35 |

Each Tuesday had more runs at 09:00Z, 05:00 ET, and two late scheduled runs. Those runs rebuild
the same files.

The answer: `stats_player` holds Monday night by about 00:35 ET Tuesday. The 05:00 ET run is a
second chance. Both land well before the 08:00 ET build.

## Question 3: play by play

### Field descriptions

Source: `https://github.com/nflverse/nflreadr/blob/main/data-raw/dictionary_pbp.csv`. The
nflfastR field description page shows the same text.

- `epa`: "Expected points added (EPA) by the posteam for the given play."
- `pass_oe`: "Dropback percent over expected on a given play scaled from 0 to 100."
- `xpass`: "Probability of dropback scaled from 0 to 1."
- `play_type`: "... no_play (timeouts and penalties), and missing for rows indicating end of
  play."

The dictionary does not say when either column is null. The source does.

### When `pass_oe` is null

Source: `https://github.com/nflverse/nflfastR/blob/master/R/helper_add_xpass.R`.

The model scores a play only if all of these hold. Otherwise `xpass` and `pass_oe` are `NA`.

1. `season >= 2006`.
2. `play_type` is `no_play`, `pass`, or `run`.
3. `posteam`, `down`, both timeout counts, `yardline_100`, and `score_differential` are not
   missing.

The code then sets `pass_oe` to `NA` when `rush == 0 & pass == 0`.

### Null counts on 2026 regular season plays

I read `play_by_play_2026.parquet` with HTTP range requests, about 1.2 MB of 7.1 MB. The file
held 16,551 rows, weeks 1 to 7, all `REG`.

| `play_type` | Rows | `pass_oe` null | `epa` null |
| --- | --- | --- | --- |
| `pass` | 6,761 | 37 | 0 |
| `run` | 4,837 | 6 | 0 |
| `no_play` | 1,761 | 1,154 | 0 |
| `kickoff` | 976 | 976 | 0 |
| `punt` | 724 | 724 | 0 |
| `extra_point` | 435 | 435 | 0 |
| `field_goal` | 395 | 395 | 0 |
| `qb_kneel` | 145 | 145 | 0 |
| `qb_spike` | 36 | 36 | 0 |
| missing | 481 | 481 | 188 |

What the nulls are:

1. All 43 pass and run rows with a null `pass_oe` are two-point tries. They have no `down`.
2. A `no_play` row has `pass_oe` only if `pass` or `rush` is 1. 607 rows do.
3. `pass_oe` is null on every special teams play, kneel, and spike.
4. `epa` is null only on rows with no `play_type`. Those are the "END QUARTER 2" and "END GAME"
   rows. "GAME" and the other "END QUARTER" rows have an `epa`.
5. Sacks keep `pass_oe`. All 434 sacks have it.

For the environment code: filter to `play_type` pass or run, and drop two-point tries. Then
every row has both `pass_oe` and `epa`.

### When the file updates after Monday night

The same run builds the play by play and `stats_player`. See the table in Question 2. The play
by play upload finished at about 04:33Z, 00:33 ET, each Tuesday. Each run held the Monday night
game. The current asset time is 2026-10-24 13:18:57Z. Source:
`https://api.github.com/repos/nflverse/nflverse-data/releases/tags/pbp`.

`play_by_play_2026.csv.gz` is 6.5 MB on 2026-10-24. It grows each week. The `.parquet` file lets
a reader fetch only the columns it needs.

## What to do in the pipeline

1. Keep the 08:00 ET build for the play by play and `stats_player`.
2. Do not trust `ffopportunity` at 08:00 ET. Check that `ep_weekly_2026.csv` has the Monday
   night `game_id`. If it does not, treat the latest week as a missing source.
3. Add `two_point_attempt != 1` to our target count, or read `targets` from `stats_player`.
4. Rescale expected points with `total_fantasy_points_exp - 0.5 * receptions_exp`.

## Not confirmed

- What starts the on-time `workflow_dispatch` runs as user `guga31bb`. It may be an outside
  scheduler. No public file in `nflverse` names it. If it stops, only the late scheduled runs
  remain. Those landed at 10:17Z to 16:53Z on Tuesdays, which is 06:17 to 12:53 ET.
- A late Monday night game. All four Monday games kicked off at 20:15 ET, more than four hours
  before the 04:30Z run. The game count shows each game in the file. The log does not show that
  each game was final. An overtime game, a delay, or a Monday doubleheader with a late kickoff may miss the
  04:30Z run. The 09:00Z run, at 05:00 ET, is the next chance.
- What `ffopportunity` holds after its Monday daytime run. Its Monday runs start before the
  Monday night game, so they cannot have it. I did not read the game count of each run.
- Whether NFL stat id 115 is ever on a `no_play` row. I could not read `play_stats_2026.rds`
  without R. The 188 of 188 match is strong evidence that it is not, but it is not the source.
- The Sleeper scoring of this league for passing and fumbles. `ffopportunity` gives 4 points per
  passing touchdown and minus 2 per interception, and leaves out fumbles. If the league differs,
  rescale `pass_fantasy_points_exp` from its parts too.
- Asset times for past weeks. GitHub keeps only the last `updated_at` of each asset. I used the
  workflow run logs in their place.
