# 07: What the CI target is, and which jobs it covers

Map: `.scratch/design-checks-speed/MAP.md`.

**Kind:** grill

**Blocked by:** 02

**Status:** done

## Question

The map set the CI `check` job to drop from about 540 s to 360 s or less. Ticket 02 found that the whole run takes 754 s, and the longest job sets that time. The notes are `02-research-baseline-times.notes.md`.

| Job | Median time |
| --- | --- |
| site-browser | 746 s, of which the Playwright test step is 666 s |
| pipeline | 375 s |
| api | 233 s |
| site-unit | 201 s |

The Bun swap speeds up only site-unit. The `node_modules` cache saves at most 3 s, because the install takes 1 to 3 s.

Decide:

1. Does the target change, or does the spec add work for site-browser and pipeline, such as Playwright shards?
2. Does the `node_modules` cache stay in the speed list, given a gain of 3 s at most?

## Decision

Brian decided on 2026-11-20 in a grill:

1. The target stays: the whole CI run takes 360 s or less, from a median of 754 s.
2. Playwright runs in shards, with `--shard=<i>/<n>` in a matrix. The projects `floor-timing` and `eggs` run one test at a time, so the spec measures the split and sets the shard count from the time.
3. The pipeline job splits into two jobs: the parallel tests with `pytest -n auto`, and the serial tests. The spec first measures each half.
4. The `node_modules` cache drops from the speed list. It saves 3 s at most and adds a cache key to maintain.

The reason: the repo is public, so more standard runners cost no money, only about 25 s of setup per job.
