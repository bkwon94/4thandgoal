# 15: CI runs the unit suite in shards and only the reachable tests on a PR

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-29, AT-30, AT-31, and AT-32.

**App:** root

**What to build:** CI runs `bun test` in a matrix of shards. The time of the full suite with each shard count sets the count. On a PR, CI runs only the tests that the diff can reach. A change to a config file, the lock file, or the test preload runs the full suite. A push runs the full suite.

**Blocked by:** 13

**Status:** in-review

- [x] The ticket records the time of the full suite with each shard count it tried, and the chosen count.
- [x] A PR that changes one file of the rankings package runs fewer test files than the full count.
- [x] A PR that changes only the lock file runs the full suite.
- [x] A push runs the full suite, and the workflow gives a push to `main` the same full run.

## Evidence

The runs are local, on the shared laptop, through the check lock. Each row gives the load average of 5 min at its start.
The real CI time gets its proof in ticket 18.

### Shard times

Each shard runs `BUN_TEST_SHARD=<i>/<n> node scripts/bun-test.mjs`, split by the time of each file in `apps/site/bun-test-timings.json`.
"4 workers" adds `--parallel=4`, the core count of an `ubuntu-latest` runner. Ticket 14 adds `--parallel` to `bun-test.mjs`.

| Shards | Workers | Time of each shard (s) | Load of each shard | Slowest shard (s) |
| --- | --- | --- | --- | --- |
| 1 | 4 | 46.7 | 4.82 | 46.7 |
| 2 | 4 | 33.8, 25.3 | 4.70, 3.77 | 33.8 |
| 3 | 4 | 33.7, 25.4, 16.6 | 4.85, 3.19, 3.33 | 33.7 |
| 4 | 4 | 18.4, 33.7, 25.5, 16.9 | 3.66, 3.34, 6.03, 4.33 | 33.7 |
| 1 | 1 | 170.0 | 3.99 | 170.0 |
| 2 | 1 | 74.0, 96.9 | 6.81, 5.63 | 96.9 |
| 3 | 1 | 70.1, 47.9, 56.0 | 5.31, 9.22, 5.95 | 70.1 |
| 4 | 1 | 37.8, 36.1, 45.6, 52.2 | 8.75, 5.67, 4.62, 4.08 | 52.2 |
| 5 | 1 | 34.3, 35.9, 33.0, 33.4, 35.2 | 4.16, 4.42, 5.90, 6.53, 5.46 | 35.9 |

A split by file count, with no timings file and 1 worker, gave a slower shard with 3 shards than with 2:

| Shards | Time of each shard (s) | Load of each shard | Slowest shard (s) |
| --- | --- | --- | --- |
| 2 | 80.9, 90.1 | 3.84, 4.54 | 90.1 |
| 3 | 93.5, 31.8, 45.3 | 3.76, 4.06, 4.07 | 93.5 |
| 4 | 28.8, 31.8, 50.1, 57.0 | 9.51, 5.90, 4.65, 3.60 | 57.0 |
| 5 | 7.1, 66.1, 22.8, 12.1, 58.4 | 2.27, 2.32, 1.96, 2.62, 2.30 | 66.1 |

`src/app/page-free.test.tsx` takes 33.5 s alone, so no shard count goes below it.
The setup of one CI job is about 42 s: the step times of the `site-unit` job of run 44656282511 on `main`.

The chosen count is 1. With 4 workers, a second shard saves 13 s, and one more job costs about 42 s of setup.
The matrix stays, so a later count is a one-line change. With 1 worker, the rule gives 2 shards: a third saves 27 s.

### The scope of a run

The list of config files is `FULL_SUITE_FILES` in `apps/site/scripts/test-scope.mjs`. `scripts/test-scope.test.mjs` tests it.

**Counts:** This ticket adds `apps/site/scripts/test-scope.test.mjs`, with 14 tests in 1 file (`bun test scripts/test-scope.test.mjs` in `apps/site`: 14 pass, 0 fail). The total is 1,808 + 14 = 1,822 tests in 194 files (AT-20).

- One rankings file: `packages/rankings/site/chapters/power-rankings.tsx` changed, and `BUN_TEST_BASE=HEAD` ran
  `bun test --isolate --changed=HEAD`. Bun printed "--changed: 1 changed file, running 1/194 test files", and the run took 25 tests across 1 file, exit 0.
  With `BUN_TEST_SHARD=<i>/3` too, shard 1 ran the 1 file, and shards 2 and 3 ran 0 files with exit 0.
- The lock file alone: `pnpm-lock.yaml` changed, and `BUN_TEST_BASE=HEAD` ran `bun test --isolate` with no `--changed`.
  The run took 1822 tests across 194 files, exit 0.
- A push: the workflow sets `BUN_TEST_BASE` only when `github.event_name` is `pull_request`, so a push to `main` sets no base.
  With no base, `make check-fast` ran `bun test --isolate`, "The run takes the full suite.", 1822 tests across 194 files.
  `scripts/test_ci_unit_shards.py` tests the condition lines.
- A plain `bun test --changed` does not see a change to `apps/site/bunfig.toml`: it ran 0 test files. That is why the full-suite list exists.
