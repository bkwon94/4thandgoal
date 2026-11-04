# 10: The rankings package

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-1 and AT-12.

**App:** both

**What to build:** The power rankings and the odds move into the `rankings` package, and its chapter comes through the chapter port. With no median game, the standings and the odds count one game a week.

**Blocked by:** 09

**Status:** ready-for-agent

- [x] The `rankings` package holds the modules of decision 01 and writes `rankings.json`.
- [x] Its chapter comes through the chapter port.
- [x] A fixture test with the median off counts one game a week in the standings and the odds, and the power form drops the median weight (AT-12).
- [x] The CPC golden diff is empty (AT-1).
