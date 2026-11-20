# 13: How many candidates does each shape give, and what do the Jev calls cost?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The fair-first Finder (handoff `.handoff/deadline-week-fair-finder.md`, rulings 1 to 3) builds four shapes: 1-for-1, 2-for-1, 3-for-1, and 3-for-2. Each side sums the trade chart values. Find the facts that the value screen (decision 14) and the Jev questions (decision 15) need.

Measure on the live week 11 snapshot, for Bo Girds and for two other CPC teams:

1. The count of candidates per shape and per partner, with no screen.
2. The count left at three or four bands of the value gap per side, such as 5, 10, and 15 percent of the larger sum.
3. The count of Jev calls per press at each band, with the questions of today plus one fairness question per candidate.
4. The cost and the rate limit of those calls, from the TypeSafe price and limits.
5. How many Spares tree candidates of today also pass each band.

Write the findings to `decisions/13-research-candidate-size-and-cost.notes.md`. Give no time claim for a press (memory `no-time-claims`).

## Decision

The facts are in `decisions/13-research-candidate-size-and-cost.notes.md`. Research found them on the live CPC rosters of 2026-11-19 and the saved week 11 chart. Brian decides the screen in 14 and the questions in 15.

1. With no screen, a press for one team has 95,092 to 242,158 candidates over 11 partners. The 3-player shapes are 91% to 94% of them.
2. A 5% band per side leaves 4,166 to 9,957. A 20% band leaves 17,585 to 42,553. No band leaves a team with zero.
3. One `fair` Noul per candidate at 5% costs $0.02 to $0.05 per press. That is 5 to 11 times the rate limit of 100k tokens per second, and a large partner passes the 64k context of one request.
4. Only 2 to 4 of the 66 to 96 Spares tree offers of today fall inside a 10% band, because QBs are low on a 1QB chart.
5. 29 of 148 pool players have no chart value and drop out. At 10%, 40% to 45% of candidates hold a player under 5 chart points. The state of today holds no chart values.
