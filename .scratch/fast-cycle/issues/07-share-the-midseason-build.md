# 07: The midseason tests share one build

Spec: `.scratch/fast-cycle/PRD.md`. Acceptance tests AT-8, AT-23, AT-24, and AT-26.

**App:** pipeline

**What to build:** The read-only midseason tests share one build per set of inputs through a session fixture. A test that writes or changes the build keeps its own build. Each assertion stays the same, and the full sim count stays. The pipeline suite then passes the same count of tests in less time than on `main`.

**Blocked by:** 01, and the merge of PR #13 into `main`. `fast-cycle` merges `main` first.

**Status:** ready-for-agent

- [ ] PR #13 has the state `MERGED` (AT-26).
- [ ] `make -C apps/pipeline test` passes the same count on `fast-cycle` and on `main`, and takes less time on `fast-cycle` (AT-23).
- [ ] The sim count of each of the three tests that need it matches `main` (AT-24).
- [ ] The diff adds no `skip`, `xfail`, or deselect, and deletes no test (AT-8).
