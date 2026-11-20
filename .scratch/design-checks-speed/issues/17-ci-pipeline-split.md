# 17: CI splits the pipeline job in two

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-33.

**App:** root

**What to build:** The pipeline job of CI splits into one job for the parallel tests and one job for the serial tests.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] The ticket records the time of each half before the split.
- [ ] One job runs the parallel pipeline tests, and another runs the serial pipeline tests.
- [ ] Each pipeline job exits 0 in 360 s or less.
