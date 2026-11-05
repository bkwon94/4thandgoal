# 01: The uneven margin

Spec: `.scratch/uneven-trade/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, and AT-4.

**App:** pipeline

**What to build:** A trade of two or more players for a larger count, such as 3-for-2 or 4-for-3, starts from sums where the 1.10 margin divides the side with more players. One player for two or more keeps the 1.25 margin. An even count gets no margin. Each start reason names the discount.

**Blocked by:** none

**Status:** in-review

- [x] A rubric test grades trade W first, test-first, and shows Bo Girds at D, 76.8 against 91.5, and Teehee at B, 91.5 against 76.8.
- [x] The tunables hold the 1.10 margin as `UNEVEN_MARGIN`, beside `CONSOLIDATION_MARGIN`.
- [x] Rubric tests cover a 4-for-3 trade at 1.10, a one-for-two trade at 1.25, and a 2-for-2 trade with no margin.
- [x] The Consolidation section of the rubric prompt names both margins.
- [x] The `analyze` target gives the results of AT-1, AT-3, and AT-4 for the real week 9 trades.
- [x] `make check-fast` passes in the pipeline.
