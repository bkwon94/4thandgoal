# Odds level: the playoff odds draw a team level, not a past score

Status: done
Date: 2026-11-02
Repos: the pipeline `cornerstone-fantasy-sleeper-weekly-report` only. The site reads the odds from the published files and does not change.
Prototype: a side-by-side of the models on the week 7 data ran on 2026-11-02. The table sits in ticket 01.

## Problem Statement

After week 7 the rankings page shows three teams at 99 percent to make the playoffs, with seven weeks
left. Brian reads that as too sure, and the prototype agrees: every model with a sane spread keeps those
teams near 94. The bigger error sits in the middle. The engine draws each future score from the team's
own seven past scores, with more weight on the last three. Seven scores are a small sample, so a team
with a wide spread gets big weeks it has no base rate for, and a team with a narrow spread never gets a
week outside its seven. At week 7 that puts a 103-point team at 54 and two 110-point teams at 42 and 49.

## Solution

Each run first draws the team's **level**: a normal around the team's season average, shrunk toward
the league average with weight n over n plus k, where n is the count of played weeks and k is a tunable
set to 5. The standard error of that level is the league spread over the square root of n plus k. Then
each remaining week's score is a normal around the level with the **league spread**: the standard
deviation of every played score from its own team's average, pooled over the league. The projection
shift stays as it is, with its gap from the raw average, because it measures the roster change and the shrink already sits in the level. The recency weight goes, because the level draw already limits the trust in a
few scores.

## Decisions

- The spread is pooled over the league, not per team. Seven scores do not pin a team's own spread.
- The shrink target is the league average of every played score.
- The random seed stays the season and the week, so a rebuild gives the same odds.
- The golden files change on purpose. The change shows in the ticket.

## Out of scope

- Strength of schedule beyond the pairs the engine already runs.
- Any change to the site, the rankings prose rules, or the swing fact.
