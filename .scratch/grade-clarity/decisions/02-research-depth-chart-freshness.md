# 02: How fresh the depth chart and the injury status are

Map: `.scratch/grade-clarity/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

The rule "steps up" reads the nflverse depth chart and the Sleeper injury status. A stale depth chart or a stale status gives a wrong Week line.

The research finds:

1. How often nflverse updates `depth_charts_<season>.csv.gz` in the season, and which week a grade on a Tuesday reads.
2. How often the daily refresh and the API read the Sleeper injury status, and how old it can be at a grade.
3. Which week the status applies to, and what is known about the next week: IR and a return week on file only, or more.

The spec needs the age of each source at a grade, and a rule for a source too old to trust.

## Decision

None yet.
