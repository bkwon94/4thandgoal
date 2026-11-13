# 14: Give ruff a config and a clean baseline

**What to build:** `uv run ruff check src tests` reports zero findings on main, and a CI step keeps it that way. Today ruff has no config and reports about 1,700 old findings, most of them line length at the default 88 columns.

**Blocked by:** None (can start immediately). Do it after the open feature branches merge, so the reformat does not conflict with them.

**Status:** done

- [ ] Add a `[tool.ruff]` section with the line length the code uses, about 120, and the rule set the team wants.
- [ ] Fix or ignore every remaining finding with a reason per ignore.
- [ ] Add a ruff step to the GitHub workflow.
- [ ] `uv run ruff check src tests` is clean. `uv run pytest -q` passes with no failed test.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in eb429ecf.
Proof: "Merge ruff-baseline: a ruff config at 120 columns and a clean baseline" is on `main`, and `make check` of the pipeline and the API runs `ruff check src tests` in CI.
Read 1 file: .scratch/todoist-queue/audit.md.
