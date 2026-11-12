# 01: The rules move to AGENTS.md

Spec: `.scratch/codex-flow/PRD.md`. Acceptance tests AT-4, AT-5, AT-6, and AT-12.

**App:** both

**What to build:** The repo rules live in `AGENTS.md` at the root and at the top of the site and the pipeline. Each `CLAUDE.md` holds only the line `@AGENTS.md`, so Claude Code reads the same rules as before and Codex reads them too. The text names `AGENTS.md` as the rules file and holds no stale `cpc:` or `~/.Codex` words. The readme rules of both apps limit `AGENTS.md` files the same way they limit `CLAUDE.md` files.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] The repo tracks three `AGENTS.md` files and three `CLAUDE.md` files, and each `CLAUDE.md` holds only `@AGENTS.md`.
- [ ] `claude -p` in the worktree answers a question about the flow from the rules, through the import.
- [ ] A grep for `cpc:` and `~/.Codex` in the three `AGENTS.md` files prints nothing.
- [ ] A staged `AGENTS.md` below the top of an app fails the readme rule of that app.
- [ ] `make check-fast` passes.
