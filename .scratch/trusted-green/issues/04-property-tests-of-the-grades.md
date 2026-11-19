# 04: Property tests of the grades

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-27 and AT-28.

**App:** pipeline

**What to build:** Hypothesis tests eight properties of the pure functions of the grades: the score range and the weight sum, the letter order, the thin depth, the league scale, the roster ranks, the position ranks, the star ranks, and the handcuff value.

**Blocked by:** none

**Status:** done

- [x] Hypothesis is a Python dev dependency in the lock file.
- [x] Each of the eight properties of the spec has one test beside the package of its function.
- [x] The tests run in the full check of each package.
- [x] A seeded `grade_letter` that gives B at 80 fails the letter-order test with a counterexample.

## Comments

Closes with the squash merge of the spec PR: `trusted-green-04` (`fb7f2148`) merged into `trusted-green` as `bd6e1616` on 2026-11-18.
Hypothesis tests cover the 8 properties in 10 tests, and AT-27 and AT-28 have PASS.
Fix D1 adds explicit examples to the letter-order test, because 500 random draws missed a seeded bug in 1 run of 3.
The builder did not count the files it read; the ticket commit changed 7 files: packages/analyzer/python/pyproject.toml, packages/analyzer/python/tests/test_properties_handcuff_value.py, packages/league/python/pyproject.toml, packages/league/python/tests/test_properties_star_ranks.py, packages/managers/python/pyproject.toml, packages/managers/python/tests/test_properties_grade.py, uv.lock.
