# 02: Codex finds the six skills and can commit

Spec: `.scratch/codex-flow/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, AT-16, AT-22, and AT-23.

**App:** both

**What to build:** Codex started at the repo root lists the six skills as `4ag:plan`, `4ag:to-spec`, `4ag:to-acceptance`, `4ag:to-tickets`, `4ag:implement`, and `4ag:review`, through one symlink each in `.agents/skills/`. A call of `$4ag:implement` loads the repo skill, not the user skill `implement`. The tracked project `.codex/config.toml` holds the profile `4ag` as the default, with write on the repo `.git`, the network on, and approval `never`. It also keeps the `scrolltide` MCP server. A Codex session can then commit in a ticket worktree and call `gh` with no prompt. A real run finds out whether Codex needs the project to be trusted first.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] `codex debug prompt-input "hi"` names the six `4ag:` skills, each with a path under the plugin skills folder.
- [ ] A Codex session log for `$4ag:implement` injects the repo skill and no user skill.
- [ ] `.agents/skills/` holds exactly six symlinks, and each resolves to the skill of the same name.
- [ ] A default Codex session commits in a probe worktree and `gh api` prints `4thandgoal`, with any trust step recorded.
- [ ] No Codex plugin manifest exists, and no skill file moves.
- [ ] `make check-fast` passes.
