# 04: The Week plan and "Try it"

Spec: `.scratch/playoff-paths/PRD.md`. Acceptance tests AT-12, AT-13, AT-20, AT-22, AT-33, and AT-34.

**App:** both

**What to build:** A tap on a Path opens its Week plan in a sheet: the header "Your plan to 15-13 · you're in N%", the order line, and one row per week left with the result, the Score to beat, and 1 or 2 games to root for. "Try it" sets the results of the plan as a What-if. The What-if route of the API returns the grown page block and the board odds, on the Tuesday inputs, with no Sleeper call. A What-if with no set result equals the file.

**Blocked by:** 03

**Status:** ready-for-agent

- [x] The Week plan of the first Path of the 4-2 Finish of Bo Girds holds 3 rows, weeks 12 to 14.
- [x] "Try it" odds equal a What-if of the plan within 1 point.
- [ ] Two equal What-if calls on the local evidence API give equal responses.
- [ ] The sheet and the set line pass the WebKit overlap check at the 4 sizes, in light and dark mode.
- [x] `make check-fast` passes.
