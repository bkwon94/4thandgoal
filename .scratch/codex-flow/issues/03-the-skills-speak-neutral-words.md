# 03: The skills speak neutral words

Spec: `.scratch/codex-flow/PRD.md`. Acceptance tests AT-7, AT-8, AT-13, AT-14, and AT-15.

**App:** both

**What to build:** Each of the six skills says "load the skill `<name>`" and "start a fresh subagent", and names no Claude-only tool. A section "The harness words" in the root `AGENTS.md` maps each phrase to Claude and to Codex: the Skill tool or a `$<name>` mention, the Agent tool or `spawn_agent` with `fork_turns: "none"`, `opus` or `gpt-6-astra` for the strong model, and `mattpocock-skills:research` or `research`. The implement skill runs the builders of a frontier in batches of at most 6 in Codex, starts the Judge with the strong model, and checks the profile `4ag` in "Before you start". The builder brief names the Node 24 step for the hook in a fresh worktree. In Codex, each skill passes its "Before you start" check, and a missing global skill or profile stops the run by name.

**Blocked by:** 01, 02

**Status:** done

- [x] A grep for "Skill tool" and "Agent tool" in the skills prints nothing.
- [x] The section "The harness words" maps each phrase, the strong model, and the `research` name for both harnesses.
- [ ] Each of the six skills passes "Before you start" in its own Codex session.
- [x] A Codex session with no `research` skill stops `$4ag:plan` and names `research`.
- [x] A Codex session with the plain `:workspace` sandbox stops `$4ag:implement`, names `4ag`, and makes no worktree.
- [x] `make check-fast` passes.

## Comments

- The smoke runs of 2026-11-12 at the main checkout root: `$4ag:to-spec`, `$4ag:to-acceptance`, `$4ag:to-tickets`, and `$4ag:implement` passed "Before you start". `$4ag:plan` stopped and named `research`, because `~/.agents/skills/` of Brian has no `research`. `$4ag:review codex-flow` stopped at its PR step, because the spec has no open PR yet. Box 3 stays open until Brian adds `research` and the spec PR is open.
- Codex hides a user skill whose `agents/openai.yaml` sets `allow_implicit_invocation: false`. Brian's `to-spec`, `to-tickets`, and `implement` do this, so the first runs of `$4ag:to-spec` and `$4ag:to-tickets` named them as missing. The harness words now map "in the available skill list" to the list or `~/.agents/skills/<name>/SKILL.md` in Codex.
- The `.git` probe is `test -w "$(git rev-parse --git-common-dir)"`. It is a read. It exits 1 under `:workspace` and 0 under the profile `4ag`.
- The main checkout holds a stale untracked `AGENTS.md`, so each run prompt pointed Codex at the harness words in this worktree. The runs on the merged spec need no such pointer.
- `~/.codex/config.toml` turns on the cached plugins `4ag@4ag-local` and `cpc@cpc-local`. Codex then lists each `4ag:` skill twice, once from `.agents/skills/` and once from `~/.codex/plugins/cache/4ag-local/`. The cache copy goes stale after a skill change.
- Closes with the squash merge of the spec PR.
