# The idle stage test pins a team name of the live data

Kind: bug
Status: in-progress
Branch: `bug-idle-stage-team-name`.
Source: the session of 2026-11-24.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The idle stage test picks a team by a name that a manager can change

Done condition: `apps/site/src/app/_routes/analyzer/idle-stage.test.tsx` passes on the cpc week 11 raw rosters, where roster 12 has a new team name.
Method: diagnosing-bugs.
Cause: the test "counts Kenneth Walker III in the row of ..." in `apps/site/src/app/_routes/analyzer/idle-stage.test.tsx` picks roster 12 by the fixed name "Teehee", but `rawTeams` in `apps/site/src/fixtures/raw-teams.ts` reads each name from `clients/cpc/published/2026/managers.json`, so a rename of roster 12 in week 11 breaks the pick.
Red: at `afca6f41` with `apps/site/src/app/_routes/analyzer/idle-stage.test.tsx` of `afca6f41`, `cd apps/site && bun test --isolate src/app/_routes/analyzer/idle-stage.test.tsx`. The loop file is the test itself, so the fix commit holds the loop and the fix together. The run had the untracked copy of `clients/cpc/data/2026/week-11/` and the staged week 11 `clients/cpc/published/2026/managers.json` of the main checkout in place. Both copies were removed after the run.

```text
TestingLibraryElementError: Unable to find an accessible element with the role "button" and name `/Teehee/`
      at chooseTeam (packages/analyzer/site/form/form-steps.ts:24:34)
      at async pickTeam (packages/analyzer/site/form/form-steps.ts:32:9)
      at async <anonymous> (apps/site/src/app/_routes/analyzer/idle-stage.test.tsx:52:11)
(fail) the idle stage > counts Kenneth Walker III in the row of Teehee after the add, with no headshot on the stage (AT-2)

 2 pass
 1 fail
Ran 3 tests across 1 file.
```

Green: at `8d75c843`, `cd apps/site && bun test --isolate src/app/_routes/analyzer/idle-stage.test.tsx`, with the same week 11 copies in place, then removed.

```text
 3 pass
 0 fail
 7 expect() calls
Ran 3 tests across 1 file.
```

`make check-fast BASE=main` at `8d75c843` passes: 1972 pass, 0 fail, across 204 files.
Test verdict: pending

## Comments
