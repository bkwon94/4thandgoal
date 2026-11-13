# 04: The pointers name 4ag:quick

Spec: `.scratch/quick-runs/PRD.md`. Acceptance tests AT-31 and AT-32.

**App:** both

**What to build:** A new agent and Brian find the quick path from the files they read first. `AGENTS.md` names `4ag:quick` in The flow, beside the spec flow. `4ag:plan` says in one line that a bug or a small change goes to `4ag:quick`. `docs/agents/issue-tracker.md` gives the shape of a quick file and its two folders. `docs/agents/codex.md` gives the one-time install step of `diagnosing-bugs` for Codex. `4ag:implement` and `4ag:review` do not change.

**Blocked by:** none

**Status:** ready-for-agent

- [x] `AGENTS.md` names `4ag:quick` in The flow.
- [x] `4ag:plan` points a bug or a small change to `4ag:quick` in one line.
- [x] `docs/agents/issue-tracker.md` gives the quick file shape, the two folders, and why a quick file has no row.
- [x] `docs/agents/codex.md` gives the install step of `diagnosing-bugs`.
- [x] The skill files of `4ag:implement` and `4ag:review` do not change.
- [x] `make check-fast` passes at the root.
