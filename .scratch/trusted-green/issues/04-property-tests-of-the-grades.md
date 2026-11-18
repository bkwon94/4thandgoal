# 04: Property tests of the grades

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-27 and AT-28.

**App:** pipeline

**What to build:** Hypothesis tests eight properties of the pure functions of the grades: the score range and the weight sum, the letter order, the thin depth, the league scale, the roster ranks, the position ranks, the star ranks, and the handcuff value.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] Hypothesis is a Python dev dependency in the lock file.
- [ ] Each of the eight properties of the spec has one test beside the package of its function.
- [ ] The tests run in the full check of each package.
- [ ] A seeded `grade_letter` that gives B at 80 fails the letter-order test with a counterexample.
