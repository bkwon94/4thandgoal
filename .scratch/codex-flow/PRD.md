# Codex flow: the 4ag skills and the repo rules run in Codex and in Claude

Status: ready-for-agent
Date: 2026-11-11
Apps: both. No product code in the site or the pipeline changes. The rule tests of each app learn the `AGENTS.md` files, and the skills that build work in each app run in both harnesses.
Spec branch: `codex-flow`.
Source: the map `.scratch/codex-flow/MAP.md` and decision tickets 01 to 05, from the sessions of 2026-11-11. ADRs 0014, 0019, 0021, and 0026.
Tickets: 01 to 06, in `issues/`.

## Problem Statement

Brian: "not be constrained to only claude for development in 4thandgoal." Today the flow from an idea to a merged spec runs only in Claude Code. The six 4ag skills tell the agent to "call the Skill tool" and to "start one subagent with the Agent tool" with `model: opus`. Codex has no tool with those names. The repo rules live in three `CLAUDE.md` files, which Codex does not read. The default Codex sandbox blocks `git commit` and the network, so `4ag:implement` cannot commit a ticket or open a PR from Codex. A Claude rate limit or outage stops all work on the repo.

Two stale, untracked copies, the root `AGENTS.md` and `apps/site/AGENTS.md`, show the cost of two sources. They still say `cpc` and point at `~/.Codex/rules/`, a path that does not exist.

## Solution

One source holds the skills and the rules, and each harness reads it through a thin adapter.

- The skills stay in `.claude/plugin/skills/`. `.agents/skills/` holds one symlink for each skill. Codex follows the symlink and lists each skill as `4ag:<name>`, the same name as in Claude, because the prefix comes from the plugin manifest above the skill.
- `AGENTS.md` holds the repo rules, at the root and at the top of each app. Each `CLAUDE.md` holds one line, `@AGENTS.md`, which Claude Code imports.
- The skill text uses neutral words: "load the skill" and "start a fresh subagent". One section of the root `AGENTS.md` maps each neutral word to the tool of each harness.
- A tracked project `.codex/config.toml` holds the permission profile `4ag`. It lets a Codex session commit and call `gh`. The GitHub ruleset on `main` keeps every agent off `main`, in either harness.
- In Codex, each ticket builder and the Judge are fresh subagents in the same session. The Judge uses the strong model of the harness.

Brian then starts Codex at the repo root and runs `$4ag:plan`, `$4ag:to-spec`, `$4ag:to-acceptance`, `$4ag:to-tickets`, `$4ag:implement`, and `$4ag:review`, with the same result as in Claude.

## User Stories

1. As Brian, I want to start Codex at the repo root and see the six 4ag skills, so that I can run the flow with no Claude session.
2. As Brian, I want each skill to have the same name in Codex as in Claude, such as `4ag:plan`, so that the docs, the tickets, and my habits name one skill.
3. As Brian, I want a call of `$4ag:implement` in Codex to load the repo skill and not my user skill `implement`, so that no spec branch runs the wrong steps.
4. As Brian, I want one edit to a skill to change it for both harnesses, so that the two never drift apart.
5. As Brian, I want one edit to the repo rules to change them for both harnesses, so that Claude and Codex follow the same flow.
6. As a Claude Code agent, I want each `CLAUDE.md` to import `AGENTS.md`, so that I read the same rules as before.
7. As a Codex agent, I want the root `AGENTS.md` and the `AGENTS.md` of each app to hold the full rules, so that I know the flow, the tracker, and the check.
8. As an agent in either harness, I want the skill text to say "load the skill" and "start a fresh subagent", so that I can follow each step with my own tools.
9. As an agent in either harness, I want one section of `AGENTS.md` to map each neutral word to my tool, so that I do not guess how to load a skill or start a subagent.
10. As a Codex agent that runs `$4ag:plan`, I want the plan skill to load `grilling`, `domain-modeling`, `research`, and `prototype` by their Codex names, so that the "Before you start" check passes when the skills exist.
11. As Brian, I want the "Before you start" check to stop with the name of a missing global skill, so that a gap on a new machine fails loud.
12. As a Codex agent that runs `$4ag:implement`, I want to start each ticket builder as a fresh subagent with its absolute worktree path, so that the builder works in the right worktree.
13. As a Codex agent that runs `$4ag:implement`, I want to run the builders of a frontier in batches of at most 6, so that the Codex limit on open subagents does not stop the build.
14. As the Judge in Codex, I want to start with no context of the build, so that my Test verdict meets ADR 0026.
15. As Brian, I want the Codex Judge to use the strong model, `gpt-6-astra`, so that the Test verdicts keep the bar of the Claude Judge on `opus`.
16. As a Codex agent, I want the session to start with the permission profile `4ag`, so that a ticket builder can commit and the PR step can call `gh`.
17. As a Codex agent that runs `$4ag:implement`, I want the skill to check the profile in "Before you start", so that a blocked sandbox stops the run with the name of the profile, not mid-build.
18. As Brian, I want the GitHub ruleset on `main` to need the `verdict` check, so that no agent in either harness pushes past the Test verdicts.
19. As Brian, I want each manual step, such as the ruleset, the Codex project trust, and the `research` skill, with exact values and a check, so that I do it once and right.
20. As Brian, I want a free check that lists the Codex skills with no model call, so that a later change to the plugin cannot drop a skill unseen.
21. As Brian, I want one real small spec to run end to end in Codex before this spec merges, so that the proof is a real PR, not a load test.
22. As a maintainer, I want a rule test to fail when a skill has no symlink, a `CLAUDE.md` does not import `AGENTS.md`, or a skill names a Claude-only tool, so that the one source stays true.
23. As a maintainer, I want the rule tests that limit `CLAUDE.md` files to treat `AGENTS.md` the same way, so that the new files do not break the readme rules.
24. As Brian, I want the stale untracked `AGENTS.md` copies replaced by the tracked files, so that no file says `cpc` or `~/.Codex/rules/`.

## Implementation Decisions

- **The source of the skills.** `.claude/plugin/skills/` stays the source (decision 01). No skill file moves. `.agents/skills/4ag-<name>` is a relative symlink to `.claude/plugin/skills/<name>` for each of the six skills.
- **The names.** Codex takes the name from the `name:` line and the prefix from the nearest `.claude-plugin/plugin.json` above the target (decision 02). So Codex lists `4ag:plan` and the other five, and a call is `$4ag:plan`. The manifest `.claude/plugin/.claude-plugin/plugin.json` with `"name": "4ag"` must stay. Without it, the bare names `implement`, `to-spec`, and `to-tickets` clash with the user skills of Brian, and a clashed `$name` loads no skill.
- **The rules files.** The root `AGENTS.md`, `apps/site/AGENTS.md`, and `apps/pipeline/AGENTS.md` hold the text that each `CLAUDE.md` holds today, made neutral to the harness. Each `CLAUDE.md` holds only `@AGENTS.md` (decision 01). The text says "AGENTS.md" where it names the rules file.
- **The neutral tool words** (decision 04, a `spec` ticket). The skill text uses two phrases and no tool name:
  - "Load the skill `<name>`" in place of "call the Skill tool for `<name>`".
  - "Start a fresh subagent" in place of "start one subagent with the Agent tool". The phrase "with the strong model" marks the Judge.
- **The harness map.** A section "The harness words" in the root `AGENTS.md` maps each phrase to each harness:
  - Load the skill: Claude uses the Skill tool. Codex uses a `$<name>` mention, or reads the `SKILL.md` of the skill.
  - Start a fresh subagent: Claude uses the Agent tool with `subagent_type: general-purpose` and never `fork`. Codex uses `spawn_agent` with `fork_turns: "none"`, at most 6 open at a time (decision 03).
  - The strong model: `opus` in Claude, `gpt-6-astra` with a high reasoning effort in Codex.
  - The global skill names that differ: `research` is `mattpocock-skills:research` in Claude.
- **The ticket builders in Codex.** A subagent keeps the cwd and the sandbox of the parent, so each builder brief names its absolute worktree path, as it does today. A frontier of more than 6 tickets runs in batches, and the skill closes each finished subagent. A subagent cannot start its own subagent, which matches the briefs today.
- **The Judge.** A fresh subagent in the same harness that built the work (decision 01). It reads only `ACCEPTANCE.md` and the evidence. The parent commits `VERDICTS.md`, as today.
- **The permission profile.** The tracked project `.codex/config.toml` holds the profile `4ag` and makes it the default (decision 05). The profile extends `:workspace`, gives write on the repo `.git`, turns on the network, and sets approval to `never`. The file also keeps the `scrolltide` MCP server that the untracked copy holds today. It holds no secret.
- **The profile check.** "Before you start" of `implement` checks that the sandbox allows a write to `.git` and a call of `gh`, with a read that changes nothing. It stops with the name of the profile if the check fails.
- **The wall on `main`.** The GitHub ruleset on `main` needs the `verdict` check, with the Repository admin role on the bypass list so `publish` can still push (decision 05). This is the hold in `docs/agents/state.md`. The spec gives it to Brian as a manual step before the Codex proof run. ADR 0019 then rests on the ruleset, the skill text, and the prek hook, not on a sandbox.
- **The rule tests.** The readme rule of each app treats `AGENTS.md` like `CLAUDE.md`: one at the root, and one at the top of each app in the site rule. A rule for the harness checks three things in the tracked files: each skill under `.claude/plugin/skills/` has a symlink in `.agents/skills/` that resolves to it, each tracked `CLAUDE.md` is exactly the import line, and no skill file names "the Skill tool" or "the Agent tool". It reports through the shared rule report, as the other rules do.
- **The manual steps of Brian,** each with exact values and a check: the GitHub ruleset on `main`; the trust of the project in Codex, if a real run shows that Codex loads the project config only for a trusted project; the skill `research` in `~/.agents/skills/`; and the removal of the stale untracked `AGENTS.md`, `apps/site/AGENTS.md`, and `.codex/config.toml` in the main checkout before the pull of `main`.

## Testing Decisions

A good test checks what a reader sees from outside: the skills that Codex lists, the files that a run writes, and the PR that a run opens. It does not check how a skill words a step. The proof uses real runs of Codex CLI 0.167.1 and a real backlog ticket. No mock.

The seams, highest first:

1. **The Codex skill list.** `codex debug prompt-input "hi"` at the repo root prints the prompt that the model sees, with no model call and no cost. Its output names the six `4ag:` skills, and each path resolves under `.claude/plugin/skills/`. This is evidence, not CI, because CI has no Codex.
2. **The rule tests.** The new harness rule and the changed readme rules run in `make check-fast` and in CI. Prior art: `apps/pipeline/tests/test_rule_readmes.py`, `apps/site/src/readme-rule.test.ts`, and `apps/pipeline/tests/test_rule_tracker.py`, which read the tracked files through `git ls-files`.
3. **The Claude Code import.** A Claude Code session in the worktree loads the rules from `AGENTS.md` through `@AGENTS.md`. The evidence is the rules that the session shows, such as the `/memory` view or a question about the flow.
4. **The smoke run of each skill in Codex.** Codex loads each of the six skills and runs its "Before you start" check, from the spec branch worktree. The evidence is the transcript of each run.
5. **The real spec in Codex.** Codex runs `week-8-fixes` 07, "the READMEs name the module an agent needs", from `$4ag:plan` to `$4ag:implement`, from the spec branch worktree, before this spec merges (decision 01). The evidence is the ticket branch, the commits, `EVIDENCE.md`, the `VERDICTS.md` from a Codex Judge on `gpt-6-astra`, and the PR. The PR of that spec waits for this spec to merge.

## Out of Scope

- A Codex plugin manifest. The `.agents/skills/` symlinks give Codex the skills with no manifest.
- A Judge in the other harness, so that Claude judges Codex work and the reverse. It brings back the Claude limit. It can come later as an option.
- A copy of the global skills in the repo. The copy drifts from the source, and the repo is public.
- A prek hook that refuses a commit on `main` except a `publish` commit. The GitHub ruleset is the wall for both harnesses. The hook can come later as a second guard.
- A move of the skills out of `.claude/`. A neutral folder name is only cosmetic, and the move breaks every path in the docs and the tickets.
- A `codex exec` path for the builders or the Judge. `spawn_agent` covers both. `codex exec` stays a fallback in the research notes.
- A change to the product code of the site, the pipeline, or the API.

## Further Notes

- No run used `gpt-6-astra` yet. The real spec run is its first use.
- Codex may load a project `.codex/config.toml` only for a trusted project. The first ticket checks it with a real run and sets the manual step from the result.
- The prek hook in a fresh worktree needs `pnpm install` and Node 24 first on `PATH`. Homebrew Node 22.17 fails on the `.ts` files of `packages/design`. Each Codex builder hits this in its own worktree, so the builder brief names it. A fix of the hook itself is a later ticket.
- The research notes hold the sources and the runs: `decisions/02-research-codex-skill-loader.notes.md` and `decisions/03-research-codex-fresh-agent.notes.md`.
