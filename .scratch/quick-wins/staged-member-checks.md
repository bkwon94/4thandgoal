# Select commit checks from staged files

Kind: quick-win
Status: done
Branch: `win-staged-member-checks`.
Source: the session of 2026-11-17.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. Select commit checks from staged files

Done condition: The commit hook uses only staged paths to select workspace members under the existing dependency and shared-file rules.
Method: tdd
Red: at `a7bd3af9` with `scripts/test_changed_apps.py` of `26352faa`, `python3 -B -m unittest discover -s scripts -p test_changed_apps.py -k TheStagedCheck`

```text
FAIL: test_only_staged_paths_choose_the_member_checks (test_changed_apps.TheStagedCheck.test_only_staged_paths_choose_the_member_checks)
+ ['scripts', 'pipeline', 'api']
- ['scripts',
-  'site',
-  'pipeline',
-  'api',
-  'packages/facts',
-  'packages/league',
-  'packages/waiver']
Ran 1 test in 0.079s
FAILED (failures=1)
```

Green: at `26352faa`, `python3 -B -m unittest discover -s scripts -p test_changed_apps.py -k TheStagedCheck`

```text
.
----------------------------------------------------------------------
Ran 1 test in 0.119s

OK
```

Test verdict: PASS

## Comments

Closes with the squash merge of the PR of `win-staged-member-checks`. Commits: `26352faa`, `e45a9450`. Date: 2026-11-17.
One focused test went red, then green, and the fast checks passed 2,071 tests.
Read 8 files: AGENTS.md, Makefile, .pre-commit-config.yaml, scripts/changed_apps.py, scripts/test_changed_apps.py, .claude/plugin/skills/quick/SKILL.md, .claude/plugin/skills/quick/format.md, .claude/plugin/skills/quick/judge.md.
