# 02: The Race page with the Goal switch and the League board

Spec: `.scratch/playoff-paths/PRD.md`. Acceptance tests AT-3, AT-4, AT-5, AT-27, AT-28, AT-29, and AT-38.

**App:** both

**What to build:** A manager opens `/sim/<season>/` and sees The Race: the title, the Goal switch with Spot, Bye, and Seed with a seed picker, and the League board as one bar chart of the odds of each team for the Goal. The weekly build writes the odds and the status of each Goal for each team, the open Goal, and a `board` block into `week-NN/sim.json`. The status follows the plain check on wins for each Goal. The bar chart is a new part from `@ui-sdk/core` in the design package, with one tab stop and arrow keys between bars. Each bar is ink at 80% strength, and Your team's bar takes the client accent with a "You" tag. The menu item reads "The Race", and the short label reads "Race". The layout follows variant D of decision 04, and the work follows the design bar.

**Blocked by:** 01

**Status:** done

- [x] `week-11/sim.json` of `cpc` holds the odds and the status of the spot, the bye, and seeds 1 to 6 for each of 12 teams, and the board block.
- [x] The open Goal of each team is the best Goal with odds of 5% or more, in the order 1 seed, bye, spot.
- [x] The status of each team for each Goal equals a check by hand.
- [x] The Goal switch and the seed picker change the board bars and order.
- [x] The page passes the WebKit overlap check at 390x660, 810x980, 1080x740, and 1280x800, in light and dark mode.
- [x] `make check-fast` passes.

## Comments

- Merged into `playoff-paths` as 8920524e, 2026-11-25. Closes with the squash merge of the spec PR.
- Proof: `make check-fast` passed at each merge, and the Judge gave PASS to each test of this ticket in `VERDICTS.md`.
