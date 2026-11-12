# 03: How Codex starts a fresh agent

Map: `.scratch/codex-flow/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

Decision 01 says the Judge is a fresh agent in the same harness. `4ag:implement` also starts a subagent for each ticket. The spec needs these facts about Codex CLI 0.167.1:

1. Can a Codex session start a subagent? If so, does the subagent start with no context of the parent session?
2. If not, does a new `codex exec` process work as the fresh agent? How does it take the prompt, and how does the parent read its output?
3. Can the parent set the model of the fresh agent? Which model fills the place of `model: opus` in `implement/judge.md`?
4. Can the fresh agent read and write files in a given worktree, and run `git` and `gh`?

Check each fact with a real run, not only the docs.

## Decision

The research of 2026-11-11 found the facts, from the Codex source at tag `rust-v0.167.1` and real runs. Notes: `decisions/03-research-codex-fresh-agent.notes.md`. Decision 01 stands: the builders and the Judge are subagents in the same Codex session.

1. **The subagent.** A Codex session has the `spawn_agent` tool, and a skill asks for it in plain words. Its `fork_turns` parameter defaults to `all`, which copies the parent history. A fresh agent needs `fork_turns: "none"`. A run showed that such a child does not see the parent prompt.
2. **`codex exec`.** A new `codex exec` process also works as a fresh agent. Its exit code is 0 even when a command in the run fails, so the parent must read the files or the last message. The skills use `spawn_agent`, not `codex exec`.
3. **The model.** `spawn_agent` takes `model` and `reasoning_effort`. `gpt-6-astra` takes the place of `opus` for the Judge. No run used `gpt-6-astra` yet.
4. **The worktree.** A child keeps the cwd and the sandbox of the parent, so each builder brief gives its absolute worktree path. The default `workspace-write` sandbox blocks `git commit` and has no network, so `gh` fails. A permission profile with write on `.git` and the network fixed both with no prompt.

Rules for the spec:

- The skill text says `fork_turns: "none"` for each builder and for the Judge.
- The Judge names `gpt-6-astra` and an effort.
- Codex keeps at most 6 child agents open, and a child cannot start a child. A frontier of more than 6 tickets runs in batches.

The permission profile brings new fog, so decision 05 holds it.
