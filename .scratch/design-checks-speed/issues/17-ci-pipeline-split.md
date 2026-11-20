# 17: CI splits the pipeline job in two

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-33.

**App:** root

**What to build:** The pipeline job of CI splits into one job for the parallel tests and one job for the serial tests.

**Blocked by:** none

**Status:** ready-for-agent

- [x] The ticket records the time of each half before the split.
- [x] One job runs the parallel pipeline tests, and another runs the serial pipeline tests.
- [ ] Each pipeline job exits 0 in 360 s or less.

## Times before the split

Laptop, M2 Pro, no other check running, 2026-11-20. Each run is `make -C apps/pipeline <target>`.

| Half | Command | Time |
| --- | --- | --- |
| Parallel | `make check-parallel` (lint, typecheck, `pytest -n auto`, 1682 tests) | 130 s |
| Serial | `make test-serial` (`pytest -p no:xdist`, 2 tests) | 6 s |

CI before the split, median of 5 green runs of `main`: the job `pipeline` took 375 s, and its test step took 342 s.
The serial half is small, so the parallel job holds nearly all of the time. The CI time of each new job gets its proof after the push of the spec.
