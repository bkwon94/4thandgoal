# 17: CI splits the pipeline job in two

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-33.

**App:** root

**What to build:** The pipeline job of CI splits into one job for the parallel tests and one job for the serial tests.

**Blocked by:** none

**Status:** in-review

- [x] The ticket records the time of each half before the split.
- [x] One job runs the parallel pipeline tests, and another runs the serial pipeline tests.
- [x] Each pipeline job exits 0 in 360 s or less.

## Times before the split

Laptop, M2 Pro, no other check running, 2026-11-20. Each run is `make -C apps/pipeline <target>`.

| Half | Command | Time |
| --- | --- | --- |
| Parallel | `make check-parallel` (lint, typecheck, `pytest -n auto`, 1682 tests) | 130 s |
| Serial | `make test-serial` (`pytest -p no:xdist`, 2 tests) | 6 s |

CI before the split, median of 5 green runs of `main`: the job `pipeline` took 375 s, and its test step took 342 s.
The serial half is small, so the parallel job holds nearly all of the time. The CI time of each new job gets its proof after the push of the spec.

## Evidence of CI

Date: 2026-11-21. Runs 44873662117, 44874144251, and 44874592510 of `check.yml` on 4d5f4d13. Time is `startedAt` to `completedAt` of each job, in seconds. Each job exits 0.

| Job | 44873662117 | 44874144251 | 44874592510 |
| --- | --- | --- | --- |
| pipeline-parallel (1) | 259 | 197 | 233 |
| pipeline-parallel (2) | 264 | 194 | 268 |
| pipeline-serial | 43 | 45 | 37 |

The slowest pipeline job is 268 s, below the limit of 360 s.
