# 02: Does Codex find a repo skill

Map: `.scratch/trusted-green/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The `verify` skill lives at `.claude/skills/verify/`. Claude Code finds a skill there. The 4ag skills run in Codex too (AGENTS.md, The harness words). Find out if Codex finds a skill in the repo, and at which path. If it needs a second path, such as `.agents/skills/`, say how both harnesses share one source.

## Decision

Research on 2026-11-18. Notes: `decisions/02-research-codex-repo-skill.notes.md`.

Codex reads a repo skill only from `.agents/skills/<name>/SKILL.md`. It never reads `.claude/skills/`. The repo already shares the 4ag skills with tracked symlinks, `.agents/skills/4ag-* -> ../../.claude/plugin/skills/*` (`7c4c956a`). So `verify` lives at `.claude/skills/verify/`, with one tracked link `.agents/skills/verify -> ../../.claude/skills/verify`. Both harnesses follow a symlinked skill folder.
