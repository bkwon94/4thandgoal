# 05: The orchestrator resolves conflicts and runs fix groups

Spec: `.scratch/fast-cycle/PRD.md`. Acceptance tests AT-19, AT-20, AT-21, AT-29, and AT-30.

**App:** both

**What to build:** In the build stage of `cpc:implement`, the orchestrator resolves a merge conflict of a ticket in the spec worktree with `resolving-merge-conflicts`, then runs `make check-fast BASE=main`. A red check resets the spec branch and only then sends the ticket back. In the review stage, the orchestrator sorts the findings into groups that share no file, and one subagent per group fixes them on a fix branch that merges back under the same rule.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] A replay of a real conflicted merge-back of `midseason-report` in a throwaway worktree resolves with no subagent started, and `make check-fast` is green (AT-19).
- [ ] A resolve that breaks `make check-fast` leaves the branch at the head before the merge and sends the failure to the ticket subagent (AT-20).
- [ ] The 35 review findings of `midseason-report` sort into groups that share no file, and a check script finds no shared file (AT-21).
- [ ] Stage 1 of the build calls no `code-review` (AT-29).
- [ ] `cpc:to-tickets` has no diff against `main` (AT-30).
