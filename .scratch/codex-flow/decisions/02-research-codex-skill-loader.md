# 02: How the Codex skill loader finds a skill

Map: `.scratch/codex-flow/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

Decision 01 puts symlinks named `4ag-<name>` in `.agents/skills/`, into `.claude/plugin/skills/<name>/`. The spec needs three facts:

1. Does Codex read the skill name from the folder name or from the `name:` line of `SKILL.md`? If it reads the `name:` line, how does `$4ag-plan` exist with no change to the Claude name?
2. Does Codex follow a symlink to a folder in `.agents/skills/`? Does it read the files beside `SKILL.md`, such as `formats.md`, through the symlink?
3. Which skill wins when a repo skill and a user skill in `~/.agents/skills/` have the same name?

Check each fact with a real run of Codex CLI 0.167.1, not only the docs.

## Decision

The research of 2026-11-11 found the facts, from the Codex source at tag `rust-v0.167.1` and real runs. Notes: `decisions/02-research-codex-skill-loader.notes.md`.

1. **The name.** Codex takes the name from the `name:` line. It adds the prefix `<plugin name>:` from the nearest `.claude-plugin/plugin.json` above the symlink target. So `.agents/skills/4ag-plan` shows as `4ag:plan`, whatever the symlink name is. Codex has no name override.
2. **The symlinks.** Codex follows a folder symlink in `.agents/skills/`. The model gets the real path and reads the sibling files, such as `formats.md`.
3. **A clash.** Codex lists a repo skill and a user skill with the same name, repo first. A plain `$name` call with a clash loads neither skill.

The facts change item 3 of decision 01. Codex calls `$4ag:plan`, the same name as Claude, not `$4ag-plan`. The goal of item 3 still holds: the Claude names stay, and no name clashes. The spec must keep `.claude/plugin/.claude-plugin/plugin.json` with `"name": "4ag"`, because the prefix comes only from it.

`codex debug prompt-input "hi"` lists every skill with no model call. The smoke check of item 7 can grep its output for the six `4ag:` names.
