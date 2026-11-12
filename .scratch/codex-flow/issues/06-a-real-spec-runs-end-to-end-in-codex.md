# 06: A real spec runs end to end in Codex

Spec: `.scratch/codex-flow/PRD.md`. Acceptance tests AT-17, AT-18, AT-19, and AT-24.

**App:** both

**What to build:** Brian and a Codex session take `week-8-fixes` 07, "the READMEs name the module an agent needs", from `$4ag:plan` to `$4ag:implement`, from the worktree of `codex-flow`, before this spec merges. Brian approves the spec steps in the Codex session. The run ends with a ticket branch merged into its own Spec branch, `EVIDENCE.md`, a `VERDICTS.md` from a fresh Codex Judge on `gpt-6-astra`, and an open PR to `main` that waits for this spec to merge. The ticket also checks that this spec changes no product code.

**Blocked by:** 03, 04, 05

**Status:** ready-for-agent

- [ ] The Spec branch of the run has a merged ticket branch, `EVIDENCE.md`, `VERDICTS.md`, and an open PR.
- [ ] The session log shows the Judge `spawn_agent` call with `fork_turns: "none"` and `gpt-6-astra`.
- [ ] The session log shows the builder `spawn_agent` call with `fork_turns: "none"` and the absolute worktree path.
- [ ] The diff of `codex-flow` against `main` touches no file under the API and no source file except a rule test or the shared rule report.
