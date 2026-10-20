# Cornerstone Weekly

This repo builds the weekly report site for the Cornerstone fantasy football league. The
data comes from Sleeper. The public site is at https://cpcfantasy.com/

## Commands

- `cornerstone build` builds the report for a week.
- `cornerstone publish` publishes the built site.
- `cornerstone rewrite --chapter <key>` rewrites one chapter.

## Tuesday runbook

1. At 8:00 the launchd job builds the report and opens the page. The job is `com.briankwon.cornerstone-weekly`. Its log is `~/Library/Logs/cornerstone-weekly/build.log`.
2. Read the page.
3. Run `cornerstone rewrite --chapter <key>` for each chapter that needs a fix.
4. Run `cornerstone publish`.
5. Share the home page link: https://cpcfantasy.com/
