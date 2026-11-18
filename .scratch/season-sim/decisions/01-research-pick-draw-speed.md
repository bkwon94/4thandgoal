# 01: How does a pick fix the winner in the draw, and how fast is the live sim?

Map: `.scratch/season-sim/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

A What-if fixes the winner of some games. The sim draws scores, so the draw must make each picked winner win. Two methods are on the table:

- (a) Keep only the runs where each pick holds. This is exact, but with many picks almost no run matches, so the sim needs many more draws.
- (b) Swap the two drawn scores of a game when the picked team loses. It is cheap, but it moves points between two teams, so the points-for tiebreak and the median game shift.

Find the method that gives honest odds within the time of one call. Check other methods too, such as a draw of the score of the picked team from the part of the normal above the score of the other team.

Also find out:

1. The time of one live sim of 10,000 runs on the Fly machine of `apps/api`, with 0, 5, and 20 picks.
2. How the Sleeper projections treat a player with a long injury in each week ahead.

Write the findings at `.scratch/season-sim/decisions/01-research-pick-draw-speed.notes.md`.

## Decision

None yet.
