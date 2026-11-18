# 01: How does a pick fix the winner in the draw, and how fast is the live sim?

Map: `.scratch/season-sim/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

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

The research decided it on 2026-11-18. The notes are in `01-research-pick-draw-speed.notes.md`.

1. **The pick method is (d), a conditional draw with a weight.** Each picked game draws its pair of scores given the order of the pick. Then each run counts with a weight: the chance that the picks hold, given the drawn levels of that run. This is self-normalized importance sampling. It carries the update of a pick into the level of each team, so a picked winner also does better in its other games. Against an exact rejection reference, its largest gap is 0.7 points at 3 picks and 0.6 at 8. Swap (b) and the plain conditional draw (c) are off by up to 2.4 points. Rejection (a) needs about 4 billion draws for 20 picks.
2. **The Mac time of 10,000 runs** with method (d): 0.64 s with 0 picks, 0.72 s with 5, and 0.92 s with 20.
3. **The Fly time is an estimate**, because Docker hung. The API machine is `shared-cpu-1x` with 1 GB. One call takes about 1 to 1.5 s while the burst balance lasts, and about 11 to 15 s at the baseline quota of 6.25 %. Ticket 03 decides the machine size.
4. **The route is a sync `def`**, so FastAPI runs it in the thread pool and the event loop does not block. The sim still holds the one vCPU, so other calls slow down while a sim runs.
5. **The API image has no `sim` package.** The spec adds it to the Dockerfile.
6. **Sleeper gives no projection for a week it expects a player out**, for each week of the absence, and our fetch drops the entry. `projected_totals` counts a missing projection as 0 and fills the slot from the bench or the pool. So the build already sees a long injury in each week of the absence, up to the expected week of return.
