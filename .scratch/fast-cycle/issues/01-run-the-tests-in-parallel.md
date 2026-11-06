# 01: The pipeline and API tests run in parallel

Spec: `.scratch/fast-cycle/PRD.md`. Acceptance tests AT-6, AT-7, AT-8, and AT-9.

**App:** pipeline

**What to build:** The full test run of the pipeline and of the API runs under `pytest-xdist` with `-n auto`, in `make test` and in `make check`. A developer gets the full pipeline suite in about 1 min on the Mac of Brian, with the same pass count as a serial run. `make check-fast` and the commit hook do not change.

**Blocked by:** none

**Status:** ready-for-agent

- [x] `pytest-xdist` is a dev dependency of the pipeline and of the API, and `uv.lock` holds it.
- [x] `make -C apps/pipeline test` passes 1579 tests in 90 s or less. A serial run with `-p no:xdist` passes the same count (AT-6).
- [x] The test target of `apps/api` passes 163 tests in 40 s or less. A serial run passes the same count (AT-7).
- [x] The diff adds no `skip`, `xfail`, or deselect, and deletes no test (AT-8).
- [ ] `make check-fast` prints the same `==>` lines as on `main`, in 30 s or less, and `prek.toml` has no diff (AT-9).
