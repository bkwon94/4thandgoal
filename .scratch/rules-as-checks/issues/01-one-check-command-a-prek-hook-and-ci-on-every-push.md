# 01: One check command, a prek hook, and CI on every push

Spec: `.scratch/rules-as-checks/PRD.md`, part 1 and "Decisions". One 0013.

**What to build:** `make check` runs lint, typecheck, and the tests. `make check-fast` runs lint, typecheck,
and the rule tests. A prek hook runs `make check-fast` on each commit. A GitHub Action runs `make check` on
every push. ADR 0009 records the rule.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] `Makefile`: `check: lint typecheck test`. A new `rules` target runs `uv run pytest -q tests/test_layers.py $(wildcard tests/test_rule_*.py)`. A new `check-fast: lint typecheck rules`. Each target has a `##` help line.
- [ ] Choice: every later rule test is named `tests/test_rule_<topic>.py`, so `make rules` finds it with no edit.
- [ ] `.pre-commit-config.yaml` at the root holds one `repo: local` hook: id `check-fast`, `entry: make check-fast`, `language: system`, `pass_filenames: false`, `always_run: true`.
- [ ] Choice: the hook runs on the whole tree, not on the staged files. The subset takes about 3 seconds, so a file list adds parts and saves nothing.
- [ ] Choice: the hook does not run `ruff --fix`. A hook that writes files makes a commit that differs from the staged change.
- [ ] `README.md` gains one setup line: `prek install`, one time per clone. Each worktree then reads its own branch's config.
- [ ] `.github/workflows/check.yml`: `on: push` with no branch filter, and `workflow_dispatch`. One job `check`, `timeout-minutes: 20`. Steps: `actions/checkout@v4`, `astral-sh/setup-uv@v6`, `uv sync --locked`, `make check`. The top comment says what it runs and why.
- [ ] `refresh.yml` does not change.
- [ ] `docs/adr/0009-the-rules-are-checks.md` states: one command, the same rules in the hook and in CI, the hook runs a subset under 30 seconds, CI runs all. Later tickets add a section each.
- [ ] `make check` passes locally. `time make check-fast` shows under 30 seconds.
- [ ] Proof of the hook: in the worktree, stage a file with an unused import and run `git commit`. The hook refuses it. Remove the file.
- [ ] Proof of the publish path: `cornerstone publish` commits this repo, so the hook runs there too. In the worktree, run `env -i HOME=$HOME PATH=$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin git commit --allow-empty -m probe`. That is the PATH of the launchd plist. The hook passes. Then drop the probe commit.
- [ ] Ask Brian before the first push of the branch. The Check run on that push is green.
- [ ] If a test fails only in CI, because it reads an untracked file or the network, fix the test here. If the fix is large, return `STUCK:` with the test name.
