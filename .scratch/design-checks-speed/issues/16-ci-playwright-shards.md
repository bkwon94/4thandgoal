# 16: CI runs Playwright in shards

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-29.

**App:** root

**What to build:** CI runs Playwright in a matrix of shards. The serial projects keep one worker. The measured split sets the shard count.

**Blocked by:** none

**Status:** ready-for-agent

- [x] The ticket records the time of each shard with each count it tried, and the chosen count.
- [x] The serial Playwright projects run with one worker.
- [ ] Each Playwright shard job exits 0 in 360 s or less.

## The measured split

Date: 2026-11-20. The source is the green run 44656282511 of `main` at 1fc0a06e, whose specs match this branch.

Method:

1. The raw log of the job site-browser gives the time of each test and the wall time of each Playwright run.
2. `PLAYWRIGHT_SHARD=<i>/<n> pnpm exec playwright test --list` gives the tests of each shard. It ran on a local build of cpc, norcal, and the midseason fixture.
3. The time of a project in a shard is its CI wall time times the share of its test time in that shard.
4. Each shard job adds the builds and the export checks, 48 s, and the job setup, 72 s. The setup was 72 to 108 s on 3 runs.

The job time of each shard, in seconds, with `floor-timing` split by test:

| Shards | Each shard | Slowest |
| --- | --- | --- |
| 1 | 740 | 740 |
| 2 | 483, 378 | 483 |
| 3 | 382, 257, 345 | 382 |
| 4 | 338, 232, 225, 309 | 338 |
| 5 | 296, 199, 200, 254, 277 | 296 |

The chosen count is 5. With 4 shards, the slowest job is 338 s, or 374 s with the worst setup of 108 s. That is above 360 s. With 5 shards, the slowest job is 296 s, or 332 s with the worst setup.

`floor-timing` had `fullyParallel: false`, so 12 of its 13 tests stayed in one shard as one file. The project now has `fullyParallel: true` and `workers: 1`. Its tests spread over the shards, and each shard still runs them one at a time.

A local run of `PLAYWRIGHT_SHARD=2/5 CLIENT=cpc pnpm check:floor` printed "Running 44 tests using 2 workers, shard 2 of 5", then "Running 3 tests using 1 worker, shard 2 of 5". Both passed.

The real CI time of each shard gets its proof after the push of the spec.
