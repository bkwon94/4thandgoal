# 10: Why the midseason-report tests add about 6 min on CI

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** research

**Blocked by:** 04

**Status:** done

## Question

The 1579 pipeline tests of `main` take 4 min 40 s locally. On CI, `midseason-report` runs 1667 tests in 10 min 39 s. The 88 extra tests, likely the sim tests, may hold most of the gap. The spec needs to know if a fixed seed and a smaller sample fix it under decision 01, or if the gap is only the slower runner.

## Decision

The research decided it on 2026-11-06. The notes are `decisions/10-research-midseason-test-time.notes.md`.

1. The new tests add about 4 min, not 6 min. On CI, `main` takes 6 min 29 s and the branch takes 10 min 39 s. The old local baseline and the slower runner made up the other 2 min.
2. The sim is not the cost. One build takes 2.2 s at 500 runs and 2.9 s at 10,000 runs. The full sim count stays, because three tests need it: `test_midseason.py:279`, `:562`, and `test_sim.py:70`.
3. The cost is about 45 full builds of the same report, one per test. Most tests only read the build.
4. This spec adds one shared session fixture for each set of inputs, so the read-only tests share a build. Each assertion stays the same. This is a cache under rule 1 of decision 01.
5. The saving is about 2 min 15 s serial. Under `pytest-xdist` a session fixture runs one time per worker, so the saving is smaller. The spec measures it with `-n auto`.
6. The tests live on `midseason-report`. Per decision 13, this spec merges after PR #13, so its ticket for the fixture starts after the merge of PR #13 into `main`.
