# Cornerstone Weekly

This repo builds the weekly report site for the Cornerstone fantasy football league. The
data comes from Sleeper. The public site is at
https://bkwon94.github.io/cornerstone-fantasy-sleeper-weekly-report-site/

## Commands

- `cornerstone build` builds the report for a week.
- `cornerstone publish` publishes the built site.
- `cornerstone rewrite --chapter <key>` rewrites one chapter.

## Tuesday runbook

1. Run `cornerstone build`.
2. Open the built page in `site/` and read it.
3. Run `cornerstone rewrite --chapter <key>` for each chapter that needs a fix.
4. Run `cornerstone publish`.
5. Open the public site and check the new week.
