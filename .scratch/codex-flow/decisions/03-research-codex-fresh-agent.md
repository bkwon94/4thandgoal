# 03: How Codex starts a fresh agent

Map: `.scratch/codex-flow/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

Decision 01 says the Judge is a fresh agent in the same harness. `4ag:implement` also starts a subagent for each ticket. The spec needs these facts about Codex CLI 0.167.1:

1. Can a Codex session start a subagent? If so, does the subagent start with no context of the parent session?
2. If not, does a new `codex exec` process work as the fresh agent? How does it take the prompt, and how does the parent read its output?
3. Can the parent set the model of the fresh agent? Which model fills the place of `model: opus` in `implement/judge.md`?
4. Can the fresh agent read and write files in a given worktree, and run `git` and `gh`?

Check each fact with a real run, not only the docs.

## Decision

None yet.
