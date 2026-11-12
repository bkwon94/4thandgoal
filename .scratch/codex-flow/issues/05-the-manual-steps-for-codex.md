# 05: The manual steps for Codex

Spec: `.scratch/codex-flow/PRD.md`. Acceptance tests AT-20 and AT-21.

**App:** both

**What to build:** `docs/agents/codex.md` lists each step that Brian does by hand, each with exact values and a check: the GitHub ruleset on `main` with the `verdict` check and the Repository admin role on the bypass list, the project trust in Codex if ticket 02 found it needed, the skill `research` in `~/.agents/skills/`, and the removal of the stale untracked `AGENTS.md`, `apps/site/AGENTS.md`, and `.codex/config.toml` in the main checkout. The agent gives Brian the ruleset step when the ticket starts, then records the ruleset with `gh api`.

**Blocked by:** 02

**Status:** ready-for-agent

- [x] The doc lists the four steps, each with exact values and a check.
- [x] `gh api` shows a ruleset on `main` that needs `verdict`, with the Repository admin role on the bypass list.
- [x] `make check-fast` passes.
