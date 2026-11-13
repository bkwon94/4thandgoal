# 06: A real spec runs end to end in Codex

Spec: `.scratch/codex-flow/PRD.md`. Acceptance tests AT-17, AT-18, AT-19, and AT-24.

**App:** both

**What to build:** Brian and a Codex session take `week-8-fixes` 07, "the READMEs name the module an agent needs", from `$4ag:plan` to `$4ag:implement`, from the main checkout root, with the `.codex/config.toml` of `codex-flow` in place, before this spec merges. Codex in a linked worktree cannot write its own gitdir. Brian approves the spec steps in the Codex session. The run ends with a ticket branch merged into its own Spec branch, `EVIDENCE.md`, a `VERDICTS.md` from a fresh Codex Judge on `gpt-6-astra`, and an open PR to `main` that waits for this spec to merge. The ticket also checks that this spec changes no product code.

**Blocked by:** 03, 04, 05

**Status:** in-review

- [ ] The Spec branch of the run has a merged ticket branch, `EVIDENCE.md`, `VERDICTS.md`, and an open PR.
- [ ] The session log shows the Judge `spawn_agent` call with `fork_turns: "none"` and `gpt-6-astra`.
- [ ] The session log shows the builder `spawn_agent` call with `fork_turns: "none"` and the absolute worktree path.
- [ ] The diff of `codex-flow` against `main` touches no file under the API and no source file except a rule test or the shared rule report.

## Comments

- The run on 2026-11-12: Brian and Codex CLI 0.167.2 ran the spec `readme-module-navigation` from `$4ag:plan` to `$4ag:implement`, at the main checkout root. Its draft PR is #37. Its ticket 01 is done, its ticket 02 is blocked, and its Judge gave 13 PASS and 4 FAIL. The evidence of AT-17 to AT-19 and AT-24 sits in `EVIDENCE.md` of this spec.
- The last of the four top-level Codex sessions ran with approval `on-request`, not `never`. The sandbox stayed `workspace-write` in each session.
