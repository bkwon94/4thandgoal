# Codex flow: map

App: both.
Spec branch: `codex-flow`.

## DESTINATION

One spec: the six 4ag skills and the repo rules run in Codex and in Claude, from one source. The goal is that development in 4thandgoal is not limited to Claude.

## DECISIONS SO FAR

- The spec covers the full flow, from `plan` to `review`, from one source with a thin adapter for each harness. `decisions/01-grill-destination-and-seams.md`.
- `.claude/plugin/skills/` stays the source, and `.agents/skills/` holds symlinks into it. `decisions/01-grill-destination-and-seams.md`.
- Codex calls each skill by the Claude name, such as `$4ag:plan`. The prefix comes from `.claude/plugin/.claude-plugin/plugin.json`, so that file stays. `decisions/02-research-codex-skill-loader.md`.
- Codex follows a folder symlink in `.agents/skills/` and reads the sibling files of a skill. `decisions/02-research-codex-skill-loader.md`.
- The Judge is a fresh agent in the same harness that built the work. `decisions/01-grill-destination-and-seams.md`.
- `AGENTS.md` holds the repo rules, and each `CLAUDE.md` imports it with `@AGENTS.md`. `decisions/01-grill-destination-and-seams.md`.
- The global skills stay global, and Brian adds `research` to `~/.agents/skills/`. `decisions/01-grill-destination-and-seams.md`.
- Codex starts each builder and the Judge with `spawn_agent` and `fork_turns: "none"`. The Judge uses `gpt-6-astra`, and at most 6 children run at a time. `decisions/03-research-codex-fresh-agent.md`.
- The project `.codex/config.toml` holds the profile `4ag`, with write on `.git` and the network. The GitHub ruleset on `main` keeps agents off it, as a manual step for Brian. `decisions/05-grill-codex-permission-profile.md`.
- The skills say "load the skill" and "start a fresh subagent", and the root `AGENTS.md` maps each phrase to each harness. `decisions/04-spec-neutral-tool-words.md`.
- The proof is a smoke run of each skill in Codex, and one real small spec that Codex runs from the spec branch before the merge. `decisions/01-grill-destination-and-seams.md`.

## NOT YET SPECIFIED

None.

## OUT OF SCOPE

- A Codex plugin manifest. The `.agents/skills/` symlinks give Codex the skills with no manifest.
- A Judge in the other harness, so that Claude judges Codex work and the reverse. It brings back the Claude limit; it can come later as an option.
- A copy of the global skills in the repo. The copy drifts from the source, and the repo is public.
- A prek hook that refuses a commit on `main` except a `publish` commit. The GitHub ruleset is the wall for both harnesses; the hook can come later as a second guard.
