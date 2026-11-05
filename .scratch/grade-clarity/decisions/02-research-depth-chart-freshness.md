# 02: How fresh the depth chart and the injury status are

Map: `.scratch/grade-clarity/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The rule "steps up" reads the nflverse depth chart and the Sleeper injury status. A stale depth chart or a stale status gives a wrong Week line.

The research finds:

1. How often nflverse updates `depth_charts_<season>.csv.gz` in the season, and which week a grade on a Tuesday reads.
2. How often the daily refresh and the API read the Sleeper injury status, and how old it can be at a grade.
3. Which week the status applies to, and what is known about the next week: IR and a return week on file only, or more.

The spec needs the age of each source at a grade, and a rule for a source too old to trust.

## Decision

Brian decided it on 2026-11-05, from the research in `02-research-depth-chart-freshness.notes.md`.

The age of each source at a grade:
- The nflverse depth chart is 3 to 27 hours old, and about 35 hours with a late cron. The 2026 file has no week, only the scrape time `dt`.
- The Sleeper injury status is 0 to 24 hours old. A grade fails before it reads an older status. The status has no week.
- The nflverse injury report holds a game status for the trade week only from the Friday report on.

The rules:
1. The Week line names no step-up when the newest depth chart `dt` is more than 48 hours before the grade. One late run passes, and a missed day stops it. `read_depth_charts` must keep `dt`.
2. Out counts for the trade week only.
3. IR, PUP, NA, and Sus count as out for both weeks of the Week line. IR is not out for the season, but an NFL player on IR misses at least 4 games. Out for the season and a return week past the next week count for both weeks too.
4. Questionable and Doubtful never count.
5. On a Tuesday and a Wednesday the status is the one of the last game, so the text says "listed Out last week".
6. The Sleeper status needs no age rule.

The spec must also cover:
- The result cache key (`packages/analyzer/python/src/analyzer/cache.py`) holds no depth chart and no status of a player on no roster. The key must hold both, or a cached grade keeps a stale Week line.
- The snapshot holds a status only for rostered players. The rule "steps up" must read the full players file, because the player ahead on the depth chart is often on no roster.
