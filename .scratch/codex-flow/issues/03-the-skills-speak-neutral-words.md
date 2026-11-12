# 03: The skills speak neutral words

Spec: `.scratch/codex-flow/PRD.md`. Acceptance tests AT-7, AT-8, AT-13, AT-14, and AT-15.

**App:** both

**What to build:** Each of the six skills says "load the skill `<name>`" and "start a fresh subagent", and names no Claude-only tool. A section "The harness words" in the root `AGENTS.md` maps each phrase to Claude and to Codex: the Skill tool or a `$<name>` mention, the Agent tool or `spawn_agent` with `fork_turns: "none"`, `opus` or `gpt-6-astra` for the strong model, and `mattpocock-skills:research` or `research`. The implement skill runs the builders of a frontier in batches of at most 6 in Codex, starts the Judge with the strong model, and checks the profile `4ag` in "Before you start". The builder brief names the Node 24 step for the hook in a fresh worktree. In Codex, each skill passes its "Before you start" check, and a missing global skill or profile stops the run by name.

**Blocked by:** 01, 02

**Status:** ready-for-agent

- [ ] A grep for "Skill tool" and "Agent tool" in the skills prints nothing.
- [ ] The section "The harness words" maps each phrase, the strong model, and the `research` name for both harnesses.
- [ ] Each of the six skills passes "Before you start" in its own Codex session.
- [ ] A Codex session with no `research` skill stops `$4ag:plan` and names `research`.
- [ ] A Codex session with the plain `:workspace` sandbox stops `$4ag:implement`, names `4ag`, and makes no worktree.
- [ ] `make check-fast` passes.
