# 07: How does the live sim hold a median result, and what does one call return?

Map: `.scratch/season-sim/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

Decision 04 makes a What-if a result of Your team for one week: win or lose its game, and above or below the median of that week. Decision 01 found a method for a pick of a game winner only: a conditional draw of the pair with a weight. A median result is a condition on one score against the median of all 12 scores of that week, so the pair method does not cover it.

Find out:

1. An honest method to hold a median result in the draw, which is exact up to sample noise and runs in about 1 s at 10,000 runs. Check whether the weight method of decision 01 extends to it, such as a weight from the chance that the score lands above the median given the levels of the run.
2. Whether the page can get all its numbers from one plain sim per call, by a split of its runs: the ladder of more wins, the four results of each week, the base odds after a loss, and the root-for rows. Only the results that the manager has set would need the conditional draw.
3. The shape of the response of one call, and its size, for the page of decision 04.

Write the findings at `.scratch/season-sim/decisions/07-research-median-result-draw.notes.md`.

## Decision

None yet.
