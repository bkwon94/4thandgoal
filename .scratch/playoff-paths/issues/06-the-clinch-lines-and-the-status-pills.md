# 06: The Clinch lines and the status pills

Spec: `.scratch/playoff-paths/PRD.md`. Acceptance tests AT-17, AT-21, AT-39, AT-40, and AT-53.

**App:** both

**What to build:** The weekly build counts every set of results of this week and writes the Clinch lines of each team for the spot and the bye into the board block. The board shows each line under its team with the copy of decision 06, and a quiet pill: green for Clinched with the best Goal locked, red for Out, none for In the hunt. The design package gains the green and red tint tokens. The What-if response holds no Clinch lines.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] The Clinch lines of `cpc` week 11 agree with a check of every set of results by hand.
- [ ] Each pill text has a contrast of 4.5:1 or more in light and dark mode.
- [ ] A What-if response holds no Clinch line.
- [ ] The playoff fixture writes no Finish list, Path, or board.
- [ ] The board passes the WebKit overlap check at the 4 sizes, in light and dark mode.
- [ ] `make check-fast` passes.
