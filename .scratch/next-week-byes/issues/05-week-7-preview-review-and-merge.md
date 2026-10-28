# 05: Week 7 preview, review, and merge

Spec: `.scratch/next-week-byes/PRD.md`, "Testing Decisions", "Out of Scope".

**What to build:** Brian reads the week 7 build with the bye lines and the new voice on the local site.
Both repos pass review against `main` and merge with `--no-ff`. Nothing publishes.

**Blocked by:** 02, 03, 04.

**Status:** ready-for-agent

- [ ] `make build WEEK=7` in the pipeline worktree passes the verifier. The page JSON has `byes` on every side.
- [ ] The site dev server in the site worktree renders that page. Brian reads every blurb and the bye lines.
- [ ] A browser pass at 390 by 844, 768 by 1024, and 1280 by 800, reduced motion on, both themes, with a named agent-browser session.
- [ ] The code-review skill runs against `main` in both repos. Its findings are fixed or filed as issues.
- [ ] Pipeline: `uv run pytest -q`, `uv run ruff check src tests`. Site: `pnpm test`, `pnpm typecheck`, `pnpm build`, `pnpm check:export`.
- [ ] Each main checkout is clean and level with origin, then `git merge --no-ff next-week-byes`. No publish of week 7.
- [ ] The untracked `AGENTS.md` from the dev server is not committed.
