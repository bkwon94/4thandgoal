# 13: Grade test gaps

**What to build:** add tests for these gaps. `grade_read` at rank 4 against 3, and at rank 9 against 10. `_against_league` with every roster equal gives 1.0, but with no chart it gives 0.0. The `GRADE_HOLE_COST` floor at four or more holes. The `GRADE_SPARE_RANK` edge, QB12 against QB13. The build test checks no field of `grade`, and not the order of `top_performers` or `best_adds`. Pipeline repo.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `grade_read` tests cover rank 4 against 3 and rank 9 against 10.
- [ ] `_against_league` tests cover every roster equal (1.0) and no chart (0.0).
- [ ] A test covers the `GRADE_HOLE_COST` floor at four or more holes.
- [ ] A test covers the `GRADE_SPARE_RANK` edge, QB12 against QB13.
- [ ] The build test checks the fields of `grade` and the order of `top_performers` and `best_adds`.
- [ ] No code logic changes. `ruff` is clean.
