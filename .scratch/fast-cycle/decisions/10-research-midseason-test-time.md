# 10: Why the midseason-report tests add about 6 min on CI

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** research

**Blocked by:** 04

**Status:** open

## Question

The 1579 pipeline tests of `main` take 4 min 40 s locally. On CI, `midseason-report` runs 1667 tests in 10 min 39 s. The 88 extra tests, likely the sim tests, may hold most of the gap. The spec needs to know if a fixed seed and a smaller sample fix it under decision 01, or if the gap is only the slower runner.

## Decision

None yet.
