# 08: The race Topic leads the front door

Spec: `.scratch/playoff-paths/PRD.md`. Acceptance tests AT-24, AT-25, and AT-26.

**App:** both

**What to build:** The playoff race Topic is the first of the 3 Suggestions in each week of the regular season, and the pin stops when week 14 is final. Its Answer adds Your team's top 3 Finishes for a playoff spot, the status pill, and the link "Open The Race" (decision 05).

**Blocked by:** 03

**Status:** ready-for-agent

- [x] The Suggestions of Bo Girds in `cpc` week 11 put the race Topic first.
- [x] A fixture that runs as week 15 does not pin the race Topic.
- [x] The race Answer shows the top 3 Finishes, no pill for a team In the hunt, and the link to `/sim/2026/`.
- [ ] `make check-fast` passes.
