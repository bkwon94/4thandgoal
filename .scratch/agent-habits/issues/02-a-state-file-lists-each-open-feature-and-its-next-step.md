# 02: A state file lists each open feature and its next step

Spec: `.scratch/agent-habits/PRD.md`, part 2.

**What to build:** `docs/agents/state.md` lists each feature under `.scratch/` with an open ticket, one line
each: the feature, the next ticket, and its blocker. A cold agent reads `CLAUDE.md`, then this file, then the
ticket. A rule test fails when a feature has an open ticket and no line, or a line and no open ticket.

**Blocked by:** `rules-as-checks` site ticket 03, the report shape. The rule test uses its helper.

**Status:** ready-for-agent

- [x] `docs/agents/state.md` has one table: Feature, Next ticket, Blocked by, Hold. Under 30 lines.
- [x] The Hold column names a date or an event, such as "week 8 page live", or is empty.
- [x] Choice: the file lists open features only. A done feature leaves the file. The tracker holds its history.
- [ ] Choice: no handoff file once this exists. `.handoff/` leaves the repo, and `CLAUDE.md` points to the
  state file under a heading "Where the work sits".
- [x] The rule test, id `tracker/state-file`, reads each `.scratch/*/issues/*.md` and its Status line. An open
  status is any status that is not done and not wontfix.
- [x] The test fails on a feature with an open ticket and no row. The fix line: "Add a row to
  `docs/agents/state.md`."
- [x] The test fails on a row with no open ticket. The fix line: "Remove the row. The feature is done."
- [x] The test runs its rule on one temporary tracker folder with one open ticket and an empty state file, and
  finds one offense.
- [ ] `docs/agents/issue-tracker.md` says: the close comment of a ticket updates the state file in the same commit.
- [ ] `pnpm check` passes.
