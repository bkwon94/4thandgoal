# 07: How does the live sim hold a median result, and what does one call return?

Map: `.scratch/season-sim/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

Decision 04 makes a What-if a result of Your team for one week: win or lose its game, and above or below the median of that week. Decision 01 found a method for a pick of a game winner only: a conditional draw of the pair with a weight. A median result is a condition on one score against the median of all 12 scores of that week, so the pair method does not cover it.

Find out:

1. An honest method to hold a median result in the draw, which is exact up to sample noise and runs in about 1 s at 10,000 runs. Check whether the weight method of decision 01 extends to it, such as a weight from the chance that the score lands above the median given the levels of the run.
2. Whether the page can get all its numbers from one plain sim per call, by a split of its runs: the ladder of more wins, the four results of each week, the base odds after a loss, and the root-for rows. Only the results that the manager has set would need the conditional draw.
3. The shape of the response of one call, and its size, for the page of decision 04.

Write the findings at `.scratch/season-sim/decisions/07-research-median-result-draw.notes.md`.

## Decision

Research, 2026-11-18. Notes: `07-research-median-result-draw.notes.md`.

**The method.** Hold a set result with the conditional draw with a weight of decision 01, in the order "Your score first". Your team beats the median exactly when its score is above r6 after a win, or above r5 after a loss. Here r1 to r10 are the other 10 scores, high to low. Draw Your score cut to its side of that line. Then draw the opponent's score cut to its side of Your score. The weight of the run is the product of the two chances. Weights of other weeks and of the picks of decision 01 multiply. Against rejection, the playoff odds agree within 0.5 to 1.4 points. With no weight, the odds are off by up to 5.4 points.

**The time.** 10,000 runs take 0.90 s with no set result and 1.10 s with 12 set results, on the Mac under load. `season_sim` takes 0.85 s on the same shape. Fly is about 1.2 to 2.2 s at 6 weeks left, an estimate. Ticket 03 sizes the machine.

**One sim per call.** One weighted sim gives each number of the page by a split of its runs: the ladder, the four results of each week, the odds after a loss, and the root-for rows. Each split is exact up to sample noise. Keep the fixed seed of `season_sim`, so the same set results give the same numbers on each call. The noise is under 1 point for a common result, and up to 4.4 points for a rare result after 2 rare results are set.

**For the spec.**

- Rank the root-for rows with a tolerance. The top 3 change order between seeds, because they sit within about 1 point. Keep a row that lifts the odds by 1 point or more, round to whole points, and break a tie by the standings.
- Return `effective_runs`. Mark a number as "about" when its chance times `effective_runs` is under 400 runs.
- The response holds `schema_version`, `season`, `week`, `runs`, `effective_runs`, `you`, `set`, `teams`, `sample`, and one `page` block. `teams` and `sample` reuse the schemas of `sim.ts`. sim.json gets a `pages` block with one `page` per team, so the page reads one shape before and after a What-if.
- The size is 44 KB gzip with 200 stored runs, and 1.6 KB with none. The stored runs are 96 % of it. The API turns on `GZipMiddleware`, because it sends no gzip now.
