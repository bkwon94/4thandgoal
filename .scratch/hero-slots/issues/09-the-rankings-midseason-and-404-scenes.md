# 09: The rankings, midseason, and 404 scenes

Spec: `.scratch/hero-slots/PRD.md`. Acceptance tests AT-19, AT-22, AT-23, and AT-35 for the report.

**App:** site

**What to build:** A manager opens `/rankings/` and sees 12 lights in the order of the power rank at their playoff odds, with the rank-1 team flared and labeled. The midseason opener and takeover show 12 lights at the season totals in the order of the standings, with the leader flared. The 404 shows lights that drift and never settle. The act titles of the report keep the static grid.

**Blocked by:** 03, 04, and 07

**Status:** done

- [x] The rankings scene of AT-19 shows, and the evidence names the rank-1 team and its odds.
- [x] The midseason scene of AT-22 shows, and the evidence names the leader.
- [x] The 404 frames at 2 s and 6 s differ, and the lights never settle (AT-23).
- [x] In the report the opener has a scene and no act title has one (AT-35).
- [x] `pnpm check:floor` passes for `cpc` and `norcal`.

## Comments

- Revision of 2026-11-08, Brian: the rankings, midseason opener, and takeover scenes leave, so those heroes keep the static grid (AT-35, AT-44). The 404 drift stays (AT-23), and the rankings hero gets the manager link of rank 1 (AT-45).
