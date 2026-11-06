# 06: One background full check in the evidence stage

Spec: `.scratch/fast-cycle/PRD.md`. Acceptance tests AT-22.

**App:** both

**What to build:** When the evidence stage of `cpc:implement` starts, the orchestrator starts one `make check` in the background in the spec worktree, and runs no other `uv run --exact --package` there meanwhile. A red run gets fixed before the push, and the fix runs only the check of the failed member again. The push does not wait on a run that is already green. This ticket merges before the evidence stage of this spec, because that stage proves it.

**Blocked by:** 01, 04

**Status:** ready-for-agent

- [x] The skill text starts `make check` in the background at the start of the evidence stage, and names the rule of one `uv run` per checkout.
- [ ] In the evidence stage of `fast-cycle`, `make check` starts within 1 min of the stage start and ends green before the push, and the push waits 0 min for it (AT-22).
