# 02: How the Codex skill loader finds a skill

Map: `.scratch/codex-flow/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

Decision 01 puts symlinks named `4ag-<name>` in `.agents/skills/`, into `.claude/plugin/skills/<name>/`. The spec needs three facts:

1. Does Codex read the skill name from the folder name or from the `name:` line of `SKILL.md`? If it reads the `name:` line, how does `$4ag-plan` exist with no change to the Claude name?
2. Does Codex follow a symlink to a folder in `.agents/skills/`? Does it read the files beside `SKILL.md`, such as `formats.md`, through the symlink?
3. Which skill wins when a repo skill and a user skill in `~/.agents/skills/` have the same name?

Check each fact with a real run of Codex CLI 0.167.1, not only the docs.

## Decision

None yet.
