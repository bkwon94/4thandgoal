# 01: The destination and the seams

Map: `.scratch/codex-flow/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

What is the one spec that this feature ends in, and which seams move so that the 4ag flow runs in Codex?

## Decision

Brian decided each item in the grill of 2026-11-11. The goal: development in 4thandgoal is not limited to Claude.

1. **The scope.** All six skills run in Codex: `plan`, `to-spec`, `to-acceptance`, `to-tickets`, `implement`, and `review`. One source holds the skills, and each harness gets a thin adapter. Two copies of 14 skill files drift apart fast.
2. **The source.** `.claude/plugin/skills/` stays the source. `.agents/skills/` holds symlinks into it. No file moves, so the history and the paths in the docs stay true.
3. **The names.** Codex calls `$4ag-plan`, `$4ag-to-spec`, and so on. Claude keeps `4ag:plan`. The bare names `implement`, `to-spec`, and `to-tickets` clash with Brian's skills in `~/.agents/skills/`.
4. **The Judge.** A fresh agent in the same harness judges the work. A Judge that must run in Claude brings back the Claude limit. A fresh agent has none of the context of the build, so it meets ADR 0026.
5. **The rules files.** `AGENTS.md` holds the rules. Each `CLAUDE.md` holds the one line `@AGENTS.md`. This covers the root, `apps/site/`, and `apps/pipeline/`. The text of the rules becomes neutral to the harness.
6. **The global skills.** `grilling`, `domain-modeling`, `research`, and `prototype` stay global. Brian adds `research` to `~/.agents/skills/` as a manual step. The check in "Before you start" stops with the name of a missing skill.
7. **The proof.** Codex loads each of the six skills and runs its "Before you start" check. Codex also runs one real small spec from `$4ag-plan` to `$4ag-implement`, such as `week-8-fixes` 07. That run is from the spec branch worktree, before the merge, so it can get a Test verdict.

Facts found in the grill:

- Codex CLI 0.167.1 is installed.
- Only `implement/judge.md` names a model, `model: opus`.
- The repo has no Claude hooks. `.claude/settings.json` only turns on the plugin. The prek hook is a git hook.
- The untracked root `AGENTS.md` and `apps/site/AGENTS.md` are stale copies that say `cpc` and `~/.Codex/rules/`.
