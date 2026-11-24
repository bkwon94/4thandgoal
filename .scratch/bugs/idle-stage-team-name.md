# The idle stage test pins a team name of the live data

Kind: bug
Status: done
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
Test verdict: PASS

## Smoke

Smoke: flow `Analyzer`. "Smoke run: 1 flow, 1 passed, 0 failed". Shots in `.scratch/bugs/idle-stage-team-name/smoke/`.

## Comments

1. Closes with the squash merge of the PR of `bug-idle-stage-team-name`. Commits: `afca6f41`, `8d75c843`, `c3e55b0c`, `e78c82c2`. Date: 2026-11-24.
2. `make check-fast BASE=main` passes with 1972 tests, and the loop of item 1 went red, then green.
3. Three Playwright specs still pick a team by a fixed live name: `apps/site/e2e/front-door-tour.spec.ts:354` (Bo Girds), `apps/site/e2e/analyzer-stage.spec.ts:312` (All You Need Is Love, The Blue Tent), and `apps/site/e2e/eggs.spec.ts:165` (Lil Fridge).
4. The test still picks the player Kenneth Walker III by name, so a trade of that player can break it the same way.
5. `chooseTeam` in `packages/analyzer/site/form/form-steps.ts:24` builds a `RegExp` from a team name with no escape.
6. Read 7 files: AGENTS.md, apps/site/AGENTS.md, .claude/plugin/skills/quick/format.md, .scratch/bugs/idle-stage-team-name.md, apps/site/src/app/_routes/analyzer/idle-stage.test.tsx, apps/site/src/fixtures/raw-teams.ts, packages/analyzer/site/form/form-steps.ts.
