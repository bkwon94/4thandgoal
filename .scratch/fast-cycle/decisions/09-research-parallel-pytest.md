# 09: Can the pipeline and API tests run under pytest-xdist

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** research

**Blocked by:** 04

**Status:** open

## Question

Decision 04 runs the pipeline tests in parallel. Some tests may share a file, a cache folder, a golden file, or a fixed port, and then fail at random under `pytest-xdist`. The spec needs to know which tests are safe, what to change, and the time on a CI runner of 4 cores. On local `main`, the 1579 pipeline tests take 4 min 40 s, and no single test dominates.

## Decision

None yet.
