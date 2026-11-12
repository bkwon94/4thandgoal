# 07: The standings ladder and the schedule strip

Spec: `.scratch/front-door-lineup/PRD.md`. Acceptance tests AT-27, AT-28, AT-40.

**App:** both

**What to build:** Playoff race shows the standings ladder: one row per team with the rank, the name, a bar of the playoff odds, and the record, with a rule at the playoff line and the row of Your team in red. Your season shows the schedule strip: a dashed step path of the ranks of the opponents over the weeks left, drawn against the playoff line, with one row per week.

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] The week 9 build of cpc writes a ladder `block` with 12 rows and the playoff line after the 6th (AT-27).
- [ ] The week 9 build writes a schedule `block` for weeks 10 to 14 (AT-28).
- [ ] Every league Topic except Position leaders and recent trades has a `block` in both leagues (AT-40).
- [ ] Site screenshots show the ladder and the strip (AT-27, AT-28).
