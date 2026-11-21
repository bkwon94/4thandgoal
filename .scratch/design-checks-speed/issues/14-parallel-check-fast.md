# 14: `make check-fast` runs in parallel with a cap for the hook

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-26 and AT-27.

**App:** root

**What to build:** `make check-fast` runs the scripts, the apps, and the packages in parallel. In the site, the lint, the format check, the type check, and the tests run in parallel after the client build. The hook caps the parallel jobs, so the site tests stay under the 5 s timeout when two commits run at once.

**Blocked by:** 03 and 13

**Status:** done

- [x] Two full runs of `make check-fast` on the quiet laptop each take 97 s or less and exit 0.
- [x] Two commits in two worktrees at the same time both pass the hook, with no 5 s timeout.

## Comments

The merge: `6f56bdab` merged into `design-checks-speed` on 2026-11-20; review fixes on fix branches a to n; Judge fix round on AT-13 (evidence only).
The proof: `make check-fast BASE=main` passed at each merge, 3 green CI runs on 4d5f4d13 gave a median of 315 s, and the Judge gave PASS to AT-1 to AT-39.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/design-checks-speed/PRD.md, .scratch/design-checks-speed/ACCEPTANCE.md, .scratch/design-checks-speed/issues/14-parallel-check-fast.md.
Closes with the squash merge of the spec PR.
