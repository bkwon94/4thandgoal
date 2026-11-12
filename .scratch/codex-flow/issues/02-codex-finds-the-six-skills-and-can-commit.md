# 02: Codex finds the six skills and can commit

Spec: `.scratch/codex-flow/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, AT-16, AT-22, and AT-23.

**App:** both

**What to build:** Codex started at the repo root lists the six skills as `4ag:plan`, `4ag:to-spec`, `4ag:to-acceptance`, `4ag:to-tickets`, `4ag:implement`, and `4ag:review`, through one symlink each in `.agents/skills/`. A call of `$4ag:implement` loads the repo skill, not the user skill `implement`. The tracked project `.codex/config.toml` holds the profile `4ag` as the default, with write on the repo `.git`, the network on, and approval `never`. It also keeps the `scrolltide` MCP server. A Codex session can then commit in a ticket worktree and call `gh` with no prompt. A real run finds out whether Codex needs the project to be trusted first.

**Blocked by:** none

**Status:** in-review

- [x] `codex debug prompt-input "hi"` names the six `4ag:` skills, each with a path under the plugin skills folder.
- [x] A Codex session log for `$4ag:implement` injects the repo skill and no user skill.
- [x] `.agents/skills/` holds exactly six symlinks, and each resolves to the skill of the same name.
- [x] A default Codex session commits in a probe worktree and `gh api` prints `4thandgoal`, with any trust step recorded.
- [x] No Codex plugin manifest exists, and no skill file moves.
- [x] `make check-fast` passes.

## Comments

- The trust step: Codex loads the project `.codex/config.toml` only for a trusted project. `~/.codex/config.toml` holds `[projects."/Users/brian.kwon/repos/4thandgoal"]` with `trust_level = "trusted"`. Before the merge, the main checkout needs a copy of this branch's `.codex/config.toml`, because Codex reads the config of the folder where it starts.
- Codex starts at the main checkout root, not in a worktree. In a linked worktree, its own gitdir stays read-only and the other worktrees sit outside its workspace.
- The `.git` grant is the absolute `~/repos/4thandgoal/.git`, because Codex 0.167.1 rejects a relative path. The prek hook needs write on `~/.cache/prek`, `~/.cache/uv`, and `~/Library/pnpm/store`.
- The proof of box 4 on 2026-11-12: a default `codex exec` at the main checkout root, with no `-c`, ran with `sandbox: workspace-write (network access enabled)` and `approval: never`. It committed `0e738e1c probe` in the probe worktree with the hook passed, and `gh api` printed `4thandgoal`. The probe worktree and branch are removed.
