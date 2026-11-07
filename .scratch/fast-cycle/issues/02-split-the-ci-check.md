# 02: One CI job per member, a gate check, and a cached Chromium

Spec: `.scratch/fast-cycle/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, AT-4, AT-5, AT-9, AT-27, and AT-28.

**App:** both

**What to build:** The workflow `Check` runs the jobs `scripts`, `site`, `pipeline`, `api`, and `packages` at the same time. A gate job named `check` needs all five and fails if one fails. The site job takes Chromium from a cache keyed on the Playwright version. A push of a spec PR gets a green or red `check` in 10 min or less. The deploys start from `workflow_run` of `Check` as before, and the root `make check` still runs every member in sequence.

**Blocked by:** 01

**Status:** in-review

- [x] The root Makefile has one target per member, and `make check` still runs them all in sequence.
- [ ] A push of `fast-cycle` gives a green `check` in 10 min or less, after one run that fills the cache (AT-1).
- [ ] The five jobs start within 1 min of the first job, and `check` needs all five (AT-2).
- [ ] A throwaway branch with one planted failed API test gives a red `api`, a red `check`, and the conclusion `failure`. The draft PR is closed and the branch deleted after the run (AT-3).
- [ ] The second run reports a cache hit, and its Chromium step takes 2 min or less (AT-4).
- [x] `deploy-sites.yml` and `deploy-api.yml` have no diff against `main` (AT-5).
- [ ] A throwaway branch that changes one doc line runs all five jobs (AT-27).
- [x] `main` still has no ruleset (AT-28).
