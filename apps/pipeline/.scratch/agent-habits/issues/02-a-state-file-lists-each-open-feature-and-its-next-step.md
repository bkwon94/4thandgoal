# 02: A state file lists each open feature and its next step

Spec: `.scratch/agent-habits/PRD.md`, part 2.

**What to build:** `docs/agents/state.md` lists each feature under `.scratch/` with an open ticket, one line
each: the feature, the next ticket, and its blocker. A cold agent reads `CLAUDE.md`, then this file, then the
ticket. A rule test fails when a feature has an open ticket and no line, or a line and no open ticket.

**Blocked by:** `rules-as-checks` pipeline ticket 04, the report shape. The rule test uses its helper.

**Status:** done

- [x] `docs/agents/state.md` has one table: Feature, Next ticket, Blocked by, Hold. Under 30 lines.
- [x] The Hold column names a date or an event, such as "week 8 page live", or is empty.
- [x] Choice: the file lists open features only. A done feature leaves the file. The tracker holds its history.
- [x] Choice: no handoff file once this exists. `.handoff/` leaves the repo, and `CLAUDE.md` points to the
  state file under a heading "Where the work sits".
- [x] The rule test, id `tracker/state-file`, reads each `.scratch/*/issues/*.md` and its Status line. An open
  status is any status that is not done and not wontfix.
- [x] The test fails on a feature with an open ticket and no row. The fix line: "add a row to
  `docs/agents/state.md`."
- [x] The test fails on a row with no open ticket. The fix line: "remove the row, because the feature is
  done."
- [x] Choice: the house fix form is one lowercase sentence.
- [x] The test runs its rule on one temporary tracker folder with one open ticket and an empty state file, and
  finds one offense.
- [x] `docs/agents/issue-tracker.md` says: the close comment of a ticket updates the state file in the same commit.
- [x] `make check` passes.

## Comments

- 2026-11-02: merged into `main` from branch `agent-habits-02-state-file`, commits 7f1038b, c865883, a56f2f1, 6bc9938, 2edb6f4, and d5f2678, with `--no-ff`. 1498 passed, 9 deselected. `make rules` runs 24 tests. The rule reads tracked tickets through `git ls-files .scratch`, so the hook and CI see one set, and no git runs in a temp folder. The branch also swept 31 tickets whose merge `git log` proves to done: known-games 01 to 07, 09, 11; next-week-byes 01 to 04; next-week-storylines 01, 02; roster-fit-depth 01 to 06; waiver 05 to 07; tone 01 to 07 on the word of tone 09. Three stay for Brian: known-games 08, tone 09, trade-grade-v3 05. This close commit moves the agent-habits row to 03. Two reviewers passed it after one fix pass. Read 14 files: the ticket, .scratch/agent-habits/PRD.md, docs/agents/issue-tracker.md, docs/agents/triage-labels.md, CLAUDE.md, tests/rule_report.py, tests/test_rule_readmes.py, tests/test_rule_suppressions.py, tests/test_offense_report.py, docs/adr/0009-the-rules-are-checks.md, pyproject.toml, Makefile, .scratch/trade-grade-v3/issues/05-rebuild-week-6.md, .scratch/known-games/issues/10-followups-from-the-final-review.md, plus the Status line of every tracked ticket.
