# The top band has no week chip

Kind: quick-win
Status: done
Branch: `win-no-week-chip`.
Source: the session of 2026-11-15.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam, it removes a part and adds no port, page, or data shape; the done condition is one sentence.

## Items

### 1. Remove the week chip from the top band

Done condition: The top band of every page shows no week chip "WK NN" and no strip of weeks, and the menu sheet keeps its week row and "Past weeks".
Method: tdd
Red: at `60e95e71` with `packages/design/site/shell/top-band.test.tsx` of `448a1368`, `cd apps/site && pnpm exec vitest run src/../../../packages/design/site/shell/top-band.test.tsx`

```text
 FAIL  ../../packages/design/site/shell/top-band.test.tsx > The top band has no week chip (AT-11) > shows no week chip and no strip of weeks, on a page that is not a week page
AssertionError: expected <summary ...>WK 08 ...</summary> to be null
 FAIL  ../../packages/design/site/shell/top-band.test.tsx > The top band has no week chip (AT-11) > shows no week chip and no strip of weeks, on the page of a week
AssertionError: expected <summary ...>WK 07 ...</summary> to be null
 FAIL  ../../packages/design/site/shell/top-band.test.tsx > The menu sheet and the top band of the front door (AT-45, AT-47) > shows no dock, and holds the menu button in the banner
AssertionError: expected <summary ...>WK 08 ...</summary> to be null
 Test Files  1 failed (1)
      Tests  3 failed | 28 passed (31)
```
Green: at `448a1368`, `cd apps/site && pnpm exec vitest run src/../../../packages/design/site/shell/top-band.test.tsx`

```text
 Test Files  1 passed (1)
      Tests  31 passed (31)
```
Test verdict: PASS

## Comments

Closes with the squash merge of the PR of `win-no-week-chip`. Commits: `60e95e71`, `448a1368`, `ec285c1f`, `12f7021e`. Date: 2026-11-15.
The test file `top-band.test.tsx` went red with 3 of 31 failed, then green with 31 of 31 passed, and `make check-fast BASE=main` passed.
The e2e floor in `apps/site/e2e/floor.spec.ts` lost its strip-of-weeks entry, and CI runs it.
Read 9 files: AGENTS.md, GLOSSARY.md, docs/agents/issue-tracker.md, docs/adr/0033-a-quick-run-skips-the-spec-flow.md, .claude/plugin/skills/quick/format.md, .claude/plugin/skills/quick/judge.md, packages/design/site/shell/week-chip.tsx, packages/design/site/shell/top-band.tsx, apps/site/src/app/shell-props.ts.
