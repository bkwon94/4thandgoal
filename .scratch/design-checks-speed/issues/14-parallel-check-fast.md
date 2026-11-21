# 14: `make check-fast` runs in parallel with a cap for the hook

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-26 and AT-27.

**App:** root

**What to build:** `make check-fast` runs the scripts, the apps, and the packages in parallel. In the site, the lint, the format check, the type check, and the tests run in parallel after the client build. The hook caps the parallel jobs, so the site tests stay under the 5 s timeout when two commits run at once.

**Blocked by:** 03 and 13

**Status:** ready-for-agent

- [x] Two full runs of `make check-fast` on the quiet laptop each take 97 s or less and exit 0.
- [x] Two commits in two worktrees at the same time both pass the hook, with no 5 s timeout.
