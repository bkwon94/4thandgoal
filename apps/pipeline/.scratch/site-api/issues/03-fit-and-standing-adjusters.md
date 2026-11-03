# 03: Fit and standing adjusters

**What to build:** The breakdown gains the first two adjusters, each capped at one step. Roster fit compares a side's best lineup before and after the trade. Standing credits a contender's win-now move or return bet and a seller's future bet, and marks the reverse. The week 6 Josh Jacobs trade is a named case: a contender's bet on a suspended star due back by week 14 earns the step up and never grades as a bad move.

**Blocked by:** 01 (Snapshot, start letter, and the analyze command)

**Status:** done

- [x] A best lineup function takes a roster and the league's slots and returns the starters by points per game over the last four completed weeks, with the position order as the tie rule. The flex slots take the position order too.
- [x] Roster fit: a lineup gain at or above the fit threshold is one step up. A loss at or above it is one step down. The side that got the single highest-value player with no lineup loss gets the step up. The depth side gets the step up only when every player it got starts.
- [x] Standing: a contender is in a playoff spot by record. A seller is more than two games out of the last spot. A team in the middle gets no step.
- [x] A contender gets a step up for a lineup gain now, or for a got player with a return week at or before week 14. A contender gets a step down for a lineup loss now in return for a player who returns after week 14 or not at all.
- [x] A seller gets a step up when it gets the highest-value player in the trade, and a step down when it gives that player for a lineup gain now.
- [x] The return week comes from the injury report in the snapshot. A suspended player's return week comes from the same field.
- [x] The fit threshold, the playoff spot count, and the seller gap join the tunable table. The rubric file gains a section per adjuster.
- [x] Each adjuster shows in the breakdown with its step and a one-line reason, in rubric order.
- [x] Tests at the grade seam: fit up, fit down, fit at the cap, the depth side with one bench player, contender return bet up, contender loss down, seller up, seller down, middle team no step. The Josh Jacobs week 6 trade asserts the contender side gets the standing step up.
- [x] `uv run pytest -q` passes with no failed test.
