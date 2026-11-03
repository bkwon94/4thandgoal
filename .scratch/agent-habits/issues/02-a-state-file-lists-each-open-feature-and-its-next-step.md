# 02: A state file lists each open feature and its next step

Spec: `.scratch/agent-habits/PRD.md`, part 2.

**What to build:** `docs/agents/state.md` lists each feature under `.scratch/` with an open ticket, one line
each: the feature, the next ticket, and its blocker. A cold agent reads `CLAUDE.md`, then this file, then the
ticket. A rule test fails when a feature has an open ticket and no line, or a line and no open ticket.

**Blocked by:** `rules-as-checks` site ticket 03, the report shape. The rule test uses its helper.

**Status:** done

- [x] `docs/agents/state.md` has one table: Feature, Next ticket, Blocked by, Hold. Under 30 lines.
- [x] The Hold column names a date or an event, such as "week 8 page live", or is empty.
- [x] Choice: the file lists open features only. A done feature leaves the file. The tracker holds its history.
- [x] Choice: no handoff file once this exists. `.handoff/` leaves the repo, and `CLAUDE.md` points to the
  state file under a heading "Where the work sits".
- [x] The rule test, id `tracker/state-file`, reads each `.scratch/*/issues/*.md` and its Status line. An open
  status is any status that is not done and not wontfix.
- [x] The test fails on a feature with an open ticket and no row. The fix line: "add a row to
  docs/agents/state.md."
- [x] The test fails on a row with no open ticket. The fix line: "remove the row, because the feature is done."
- [x] The test runs its rule on one temporary tracker folder with one open ticket and an empty state file, and
  finds one offense.
- [x] Choice: the house fix form is one lowercase sentence.
- [x] `docs/agents/issue-tracker.md` says: the close comment of a ticket updates the state file in the same commit.
- [x] `pnpm check` passes.

## Comments

- 2026-11-02: merged into `main` from branch `agent-habits-02-state-file`, commits 4ca7e67, dfd7e4e, 6c1b439, and d78b883, with `--no-ff`. 565 tests pass, `pnpm check` green. The rule reads tracked tickets through `git ls-files`, so the hook and CI see one set. The temp-folder test runs git with `GIT_DIR`, `GIT_INDEX_FILE`, and `GIT_WORK_TREE` removed from the env, so the prek hook cannot make it write the real index. This close commit removes the `agent-habits` row, because this was its last open ticket. Finding: 12 features are open by their Status lines, and about 8 of them shipped: rankings, site-foundation, site-pages, site-report, manager-pages, next-week-byes, site-speed, waiver. A sweep ticket should close them. Two reviewers passed it after one fix pass. Read 13 files: the ticket, .scratch/agent-habits/PRD.md, docs/agents/issue-tracker.md, CLAUDE.md, src/suppression-rule.test.ts, src/readme-rule.test.ts, src/rule-report.ts, package.json, vitest.config.ts, docs/adr/0016-the-rules-are-checks.md, .handoff/rules-as-checks.md, .scratch/rankings/issues/01-reader-and-route.md, .scratch/win-win/issues/06-shared-api-call-hook.md.
