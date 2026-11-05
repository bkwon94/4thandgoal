# Notes for 02: how fresh the depth chart and the injury status are

Research of 2026-11-04. Ticket: `decisions/02-research-depth-chart-freshness.md`. All times are UTC unless the text says ET. ET after 2026-11-01 is UTC-5.

## Summary

1. The depth chart on the API is 3 to 27 hours old at a grade by design, and about 35 hours old when the daily cron starts late. The age is the same on a Tuesday and on a Saturday.
2. The Sleeper status is 0 to 24 hours old at a grade. A failed fetch of an old file fails the grade, so the status is never older than 24 hours.
3. The status has no week. On a Tuesday, "Out" is the status of the last game. For the next week, the data knows only IR, Out for the season, and the hand-kept Returns file.
4. The nflverse injuries file holds no game status for the trade week on a Tuesday. On a Saturday it holds the final Friday report for the Sunday games, so it can serve as a second source then.
5. Proposed rule: the Week line names no step-up when the newest depth chart snapshot is more than 48 hours older than the grade. "Out" counts for the trade week only. IR counts for both weeks.

## Q1. How often nflverse updates the depth chart

- The nflverse job `Update-Depth-Charts` in `nflverse/nflverse-rosters` scrapes ESPN once per run and puts the new snapshot on top of the old file. Source: https://github.com/nflverse/nflverse-rosters/blob/main/exec/update-depth-charts.R (lines 4, 36-37), https://github.com/nflverse/nflverse-rosters/blob/main/.github/workflows/update_depth_charts.yaml (line 4: cron `7 7 * * *`).
- The job runs twice a day in practice. A `workflow_dispatch` run starts at 06:00 or 07:00 UTC, about 01:00 to 02:00 ET. The scheduled run of 07:07 UTC starts late, between 13:07 and 16:57 UTC in the last ten days. Source: `gh api repos/nflverse/nflverse-rosters/actions/workflows/update_depth_charts.yaml/runs`, runs of 2026-10-26 to 2026-11-04.
- The release asset `depth_charts_2026.csv.gz` has `updated_at` 2026-11-04T15:21:06Z, and `timestamp.json` says "2026-11-04 10:21:03 EST". Source: https://github.com/nflverse/nflverse-data/releases/tag/depth_charts, and `gh api repos/nflverse/nflverse-data/releases/tags/depth_charts`.
- Our cache in the main checkout, `data/nfl/cache/nflverse/depth_charts_2026.csv.gz`, has 274 snapshots from 2026-03-22T06:38:42Z to 2026-11-03T07:02:07Z. The newest snapshot is from early Tuesday 2026-11-03, about 02:02 ET, after the games of week 8. That is the start of the trade window of week 9. The cache missed the run of 2026-11-03T14:58Z, so the download came between 07:02Z and 15:00Z on 2026-11-03.
- Every day from 2026-09-02 to 2026-11-03 has a snapshot. No day is missing.
- Each snapshot has 128 skill groups: 32 teams times QB, RB, WR, TE. WR has one ESPN slot, "Wide Receiver", so each team has one WR at rank 1 and the order is one list.
- The chart changes most on Tuesday and on Sunday. From 2026-09-02 to 2026-11-03, the sum of changed skill groups by weekday in ET is: Mon 64, Tue 159, Wed 86, Thu 47, Fri 45, Sat 37, Sun 141. A change in the top two of a group: Mon 20, Tue 31, Wed 22, Thu 14, Fri 8, Sat 10, Sun 18. The second run of a day changes nothing on most days. Source: the script `dc.py` in the scratchpad, run on the cache file.
- A player listed Out or IR stays on the chart. Of 90 IR and 87 Out skill players in the Sleeper file, 83 IR and 77 Out are on the newest nflverse snapshot. 23 of them are at rank 1 or 2, for example Jake Ferguson DAL TE rank 1 Out, and Mike Evans SF WR rank 1 Out. So "the player directly ahead is Out or IR" is a real case each week.
- Schema: 2025 and 2026 use the ESPN shape `dt,team,player_name,espn_id,gsis_id,pos_grp_id,pos_grp,pos_id,pos_name,pos_abb,pos_slot,pos_rank`. These files have no `week` column. The only time field is `dt`, the time of the scrape. 2024 and earlier use the NFL shape `season,club_code,week,game_type,depth_team,...`, with one chart per week. Source: header rows of `depth_charts_2024.csv.gz` and `depth_charts_2025.csv.gz` from the release, and of our 2026 cache.
- The nflreadr docs still say "Loads depth charts for each NFL team for each week back to 2001" and "A tibble of week-level depth charts". This is not true for 2025 and 2026. Source: https://github.com/nflverse/nflreadr/blob/main/R/load_depth_charts.R (lines 1-3, 21).
- Our reader keeps only the newest `dt` and gives no time back. Source: `packages/league/python/src/league/nflverse.py:243-265`. A rule on the age needs the reader to give `dt` too.

## Q2. How often the refresh and the API read the Sleeper status

- The status comes from the Sleeper players file `GET /v1/players/nfl`, about 16 MB on disk. The cache keeps it 24 hours. Source: `packages/league/python/src/league/provider/sleeper.py:28-30`, `:91-102`.
- Each live fetch reads the players file through `_league_raw`. This is each grade, each teams request, and the refresh route. Source: `sleeper.py:206`, `:244-262`; `packages/league/python/src/league/live.py:275`, `:312`; `apps/api/src/cornerstone_api/sources.py:62-68`.
- The API does not fetch the status live per grade. It reads the cache file, and it fetches a new file only when the file is 24 hours old or older. The first request after 24 hours pays for the fetch.
- The daily refresh does not force a new players file. It sets `max_age_seconds=0` for the nflverse files only. The players file keeps its own 24-hour rule. Source: `apps/api/src/cornerstone_api/refresh.py:16-19`, `live.py:212`, `live.py:219`.
- A failed fetch of an old players file raises, because `_get` calls `raise_for_status` and `_players` has no fallback. So a grade never reads a status older than 24 hours. It fails. Source: `sleeper.py:61-64`, `:91-102`.
- Sleeper asks for this call "once per day at most". Sleeper also gives a filter `?position=QB`, which gives a much smaller file. Source: https://docs.sleeper.com/ (section "Fetch all players").
- Age at a grade: 0 to 24 hours, on any day. How fast Sleeper itself changes a status after the NFL report: not found.
- The file holds `depth_chart_order` and `depth_chart_position` too, at the same age as the status. 85 of 87 Out and all 90 IR skill players have a `depth_chart_order`. This is a second depth chart. Its source and its update time are not documented.

## Q3. Which week the status applies to

- `injury_status` has no week field. The fields are `injury_status`, `injury_body_part`, `injury_start_date`, `injury_notes`, `status`, and `news_updated`. Source: the keys of `data/nfl/cache/players.json`.
- On Tuesday 2026-11-03 the status is the status of the last game. Examples from the file:
  - A.J. Brown NE: Questionable on the week 8 report, Out in Sleeper, news 2026-11-02T17:15Z. NE played week 8 on 2026-11-01.
  - Mike Evans and Deebo Samuel Sr. SF: Out since 2026-10-27T05:30Z. SF had a bye in week 8, so the status carries over the bye into week 9.
  - The file has 87 Out and only 19 Questionable skill players. That count matches a status after game day, not a new report.
- So a Tuesday grade that reads "Out" reads last week. Out can turn into a full practice on Wednesday.
- For the next week, the data knows these facts and no more:
  - IR, PUP, NA, and Sus in Sleeper. `OUT_STATUSES` holds Out, IR, NA, Sus, PUP. Source: `packages/league/python/src/league/ranks.py:25`.
  - The Returns file: the return week by player id, kept by hand and shared by each client. Source: `packages/league/python/src/league/paths.py:63-65`, `GLOSSARY.md:911-913`. On Fly a deploy copies it again on each boot. Source: `apps/api/deploy/entrypoint.sh:3`. Now it holds one row: `{"5850": 7}`, a week already past.
  - The "season" mark in the Returns file: out for the season. Source: `packages/league/python/src/league/snapshot.py:285-300`.
  - Due back: a player with an out status and no Returns row counts as back at the return-by week, the last regular week. Source: `ranks.py:134-152`, `packages/league/python/src/league/league_settings.py:113-117`. This is a default for the letter. It is not a fact about the next week.
- The snapshot holds a status only for rostered players. Source: `packages/league/python/src/league/parse.py:170-176`, and the comment at `ranks.py:148`. The player ahead on a depth chart is often on no roster, so the step-up rule must read the raw players file.

## Q4. The nflverse injuries file as a second source

- The job `update-injuries` reads the official NFL injury API through `nflapi::nflapi_injuries`. Its cron is `7 7 * 1,2,9,10,11,12 *`, and it runs twice a day as the depth chart job does. Source: https://github.com/nflverse/nflverse-rosters/blob/main/exec/update-injuries.R (line 6), https://github.com/nflverse/nflverse-rosters/blob/main/.github/workflows/update_injuries.yaml (line 4), and the run list of the workflow.
- The release asset `injuries_2026.csv.gz` has `updated_at` 2026-11-04T15:21:18Z. Source: https://github.com/nflverse/nflverse-data/releases/tag/injuries.
- The file has a `week` column and `report_status` with Out, Doubtful, and Questionable. It has no IR. Week 8 in our cache: 50 Out, 3 Doubtful, 79 Questionable, 188 blank. Source: our cache file, and `nflverse.py:131-142`.
- On Wednesday 2026-11-04 at 15:21Z, the live file has 28 rows for week 9, only BAL and JAX, the Thursday game. Each row has a practice status and no `report_status`. Source: a fresh download of the release asset.
- So a Tuesday grade gets no game status for the trade week. A Saturday grade gets the final Friday report for the Sunday games, if the nflverse run of about 02:00 ET Saturday is done. The time of the NFL Friday report comes from common knowledge. I did not check it at a primary source.
- The API refreshes this file in the daily refresh and at a grade when the file is 6 hours old. Source: `live.py:63-68`, `live.py:96-112`, `packages/league/python/src/league/tunables.py:39-42`.
- The slow sources read the file for the week before the trade week. Source: `packages/league/python/src/league/slow_sources.py:85-91`. The reader keeps every week, so a step-up rule can read the trade week from the same dict.
- It can serve as a second source for the trade week, from the Friday report on. It cannot serve for the next week, and it has no IR.

## Q5. Proposed rule for a source too old to trust

1. Name no step-up when the newest depth chart `dt` is more than 48 hours before the grade.
   - Reason: the normal worst case is about 35 hours. That is 27 hours by design plus the start delay of about 8 hours seen on the daily cron. 48 hours lets one late run pass. It stops a chart after a missed day, or after a failed fetch that keeps the old file (`nflverse.py:54-69`).
   - The rule needs `read_depth_charts` to give `dt` back.
2. Count "Out" for the trade week only. Count IR, and Out for the season, for the trade week and the next week. Count a Returns row with a return week after the next week for both weeks.
   - Reason: Sleeper gives no week, and on a Tuesday "Out" is the last game. No source knows "Out" for the next week.
3. Add no age rule for the Sleeper status. The grade fails before it reads a status older than 24 hours.
4. Option for Brian: on Tuesday and Wednesday, a Sleeper "Out" could show as "listed Out last week". From the Friday report on, the nflverse `report_status` could confirm it.

## Table

| Source | Who refreshes it | How often | Age at a Tuesday grade | Age at a Saturday grade |
| --- | --- | --- | --- | --- |
| nflverse depth chart, release | nflverse job `Update-Depth-Charts` | Twice a day: about 01:00-02:00 ET, and between 08:00 and 12:00 ET | n/a | n/a |
| nflverse depth chart, API copy | Daily refresh `refresh.yml`, cron 10:00 UTC with `max_age_seconds=0`; any grade when the file is 24 hours old | Once a day | 3 to 27 hours by design; about 35 hours with a late cron. A grade before the refresh reads the Monday chart, which misses the Tuesday changes | 3 to 27 hours; about 35 hours with a late cron |
| Sleeper players file, `injury_status` | First live request after the file is 24 hours old: a grade, a teams request, or the refresh route | Once a day at most | 0 to 24 hours. Content: the status of the last game | 0 to 24 hours. Content: the Friday report, if Sleeper has it. Not checked |
| nflverse injuries, API copy | Daily refresh; any grade when the file is 6 hours old | Up to four times a day | 0 to 6 hours. No row with a game status for the trade week | 0 to 6 hours. The file holds the Friday report after the run of about 02:00 ET |
| Returns file | Brian or the commissioner by hand; a deploy copies it to Fly | By hand | The age of the last edit | The age of the last edit |

Sources for the table: `.github/workflows/refresh.yml:1`, `:11`; `apps/api/src/cornerstone_api/refresh.py:16-19`; `live.py:63-68`, `:96-112`; `sleeper.py:28-30`, `:91-102`; `tunables.py:39-42`; `entrypoint.sh:3`; the nflverse run lists above.

The daily refresh has one scheduled run so far. It started 2026-11-04T17:51:57Z, 7 hours 52 minutes after its cron time. Source: `gh run list --workflow refresh.yml`, run 41881203323. The 35-hour figure rests on this one run.

The weekly build runs on the Mac at 08:00 ET each Tuesday. Source: `apps/pipeline/launchagents/com.briankwon.cornerstone-weekly.plist:14-22`, `apps/pipeline/bin/cornerstone-build:55`. It uses the cache of the main checkout, not the cache of the API. The API copy on Fly is the one a grade reads (`live.py:60-62`).

## Limits

1. I could not see the cache on the Fly volume. The ages in the table come from the code and the run times, not from the files on Fly.
2. All files in the main checkout cache have the time 2026-11-04 22:17:00. That is the time of the move into `clients/`, not of the download. So I used the content: the newest `dt`, and the newest `news_updated`, 2026-11-03T08:30:52Z.
3. I could not find how fast Sleeper changes `injury_status` after an NFL report, or where Sleeper gets `depth_chart_order`. The Sleeper docs do not say.
4. I did not check the time of the NFL injury reports at a primary source. The NFL operations page gave no text.
5. The daily refresh has only one scheduled run, so the cron delay rests on one sample.
6. The result cache key holds no depth chart and no status of a player on no roster in the trade. Source: `packages/analyzer/python/src/analyzer/cache.py:30-50`, `:52-110`. A Week line in a cached grade can stay after the chart or the status changes. The spec must add both to the key.
7. My weekday counts of chart changes use UTC-5 for the whole range. Before 2026-11-01 the true offset was UTC-4. The 06:00Z snapshot is near midnight ET, so a few changes can sit one day off.
8. The map names Out and IR only. Sleeper also gives PUP, NA, Sus, and DNR. The spec must say if these count.
