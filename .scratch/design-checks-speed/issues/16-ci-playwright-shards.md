# 16: CI runs Playwright in shards

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-29.

**App:** root

**What to build:** CI runs Playwright in a matrix of shards. The serial projects keep one worker. The measured split sets the shard count.

**Blocked by:** none

**Status:** done

- [x] The ticket records the time of each shard with each count it tried, and the chosen count.
- [x] The serial Playwright projects run with one worker.
- [x] Each Playwright shard job exits 0 in 360 s or less.

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

## The split after the first CI runs

Date: 2026-11-21. The source is run 44871380504 on 3a100c90, with 6 shards and the built-in split of Playwright.

The jobs took 363, 262, 213, 255, 317, and 326 s. Shard 1 was over 360 s. Each job holds about 120 s of setup and builds.

The built-in split gives each shard one block of tests in a row, by count. The first file of a run is slow, so its tests all landed in shard 1. The raw log of shard 1 shows it:

| Run | Shard 1 | Other shards |
| --- | --- | --- |
| `rules` | 66 s, all 9 tests of `evidence-rules.spec.ts` | 4 to 32 s |
| `floor` of cpc | 65 s, 42 tests of `analyzer-stage.spec.ts` | 27 to 108 s |
| `floor` of norcal | 54 s, 40 tests of `analyzer-stage.spec.ts` | 15 to 60 s |

The fix is the reporter `apps/site/scripts/playwright-shard-reporter.mjs`. It gives each shard each Nth test of the run, so each slow file spreads over the shards. It keeps each file of `eggs` whole, because that project is not fully parallel. The matrix now has 7 shards.

The model uses the CI time of each test in the 6 logs, and a fit of the wall of each run to the old jobs. It predicts these job times:

| Split | Each shard | Slowest |
| --- | --- | --- |
| Each Nth test, 6 shards | 309, 281, 325, 288, 281, 277 | 325 |
| Each Nth test, 7 shards | 249, 306, 266, 263, 274, 248, 296 | 306 |

A shard that holds one of the two 47 s tests of `evidence-rules.spec.ts` stays near 300 s. The `--list` of each run with `PLAYWRIGHT_SHARD=<i>/7` gives each test once: the union of the 7 shards equals the full list, with no duplicate.

## Evidence of CI

Date: 2026-11-21. Runs 44873662117, 44874144251, and 44874592510 of `check.yml` on 4d5f4d13. Time is `startedAt` to `completedAt` of each job, in seconds. Each job exits 0.

| Job | 44873662117 | 44874144251 | 44874592510 |
| --- | --- | --- | --- |
| site-browser (1) | 266 | 237 | 258 |
| site-browser (2) | 330 | 275 | 302 |
| site-browser (3) | 231 | 254 | 267 |
| site-browser (4) | 270 | 284 | 304 |
| site-browser (5) | 261 | 289 | 254 |
| site-browser (6) | 260 | 265 | 216 |
| site-browser (7) | 342 | 270 | 296 |

The slowest shard job is 342 s, below the limit of 360 s.

## Comments

The merge: `51a458b2` merged into `design-checks-speed` on 2026-11-20; review fixes on fix branches a to n; Judge fix round on AT-13 (evidence only).
The proof: `make check-fast BASE=main` passed at each merge, 3 green CI runs on 4d5f4d13 gave a median of 315 s, and the Judge gave PASS to AT-1 to AT-39.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/design-checks-speed/PRD.md, .scratch/design-checks-speed/ACCEPTANCE.md, .scratch/design-checks-speed/issues/16-ci-playwright-shards.md.
Closes with the squash merge of the spec PR.
