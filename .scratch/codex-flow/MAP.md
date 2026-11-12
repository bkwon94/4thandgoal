# Codex flow: map

App: both.
Spec branch: `codex-flow`.

## DESTINATION

One spec: the six 4ag skills and the repo rules run in Codex and in Claude, from one source. The goal is that development in 4thandgoal is not limited to Claude.

## DECISIONS SO FAR

- The spec covers the full flow, from `plan` to `review`, from one source with a thin adapter for each harness. `decisions/01-grill-destination-and-seams.md`.
- `.claude/plugin/skills/` stays the source, and `.agents/skills/` holds symlinks into it. `decisions/01-grill-destination-and-seams.md`.
- Codex calls each skill with the prefix, such as `$4ag-plan`, and Claude keeps `4ag:plan`. `decisions/01-grill-destination-and-seams.md`.
- The Judge is a fresh agent in the same harness that built the work. `decisions/01-grill-destination-and-seams.md`.
- `AGENTS.md` holds the repo rules, and each `CLAUDE.md` imports it with `@AGENTS.md`. `decisions/01-grill-destination-and-seams.md`.
- The global skills stay global, and Brian adds `research` to `~/.agents/skills/`. `decisions/01-grill-destination-and-seams.md`.
- The proof is a smoke run of each skill in Codex, and one real small spec that Codex runs from the spec branch before the merge. `decisions/01-grill-destination-and-seams.md`.

## NOT YET SPECIFIED

- Does Codex read a skill name from the folder or from the `name:` line, and do both loaders follow a symlink to a folder? `decisions/02-research-codex-skill-loader.md`.
- Can Codex start a fresh Judge agent, with which model, and how does `codex exec` take a prompt and read files? `decisions/03-research-codex-fresh-agent.md`.
- Which neutral words replace "the Skill tool" and "the Agent tool" in the skill text? `decisions/04-spec-neutral-tool-words.md`.

## OUT OF SCOPE

- A Codex plugin manifest. The `.agents/skills/` symlinks give Codex the skills with no manifest.
- A Judge in the other harness, so that Claude judges Codex work and the reverse. It brings back the Claude limit; it can come later as an option.
- A copy of the global skills in the repo. The copy drifts from the source, and the repo is public.
