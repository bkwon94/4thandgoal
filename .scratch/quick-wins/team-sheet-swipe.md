# The team sheet closes on a swipe down

Kind: quick-win
Status: done
Branch: `win-team-sheet-swipe`.
Source: the session of 2026-11-16.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam, because the team sheet moves onto the shared `Sheet` of `packages/design/site/ui/sheet.tsx`; each done condition is one sentence.

## Items

### 1. A swipe down closes the team sheet on a change of team

Done condition: On a change of team, the team sheet of the front door is the shared `Sheet` of the menu, and a drag down on it closes it and keeps the old team, while the sheet of the first visit still has no close.
Method: tdd
Red: at `0d840e00` with `apps/site/src/app/front-door/team-sheet.test.tsx` and `packages/design/site/ui/sheet-drag-jsdom.ts` of `f31db328`, `cd apps/site && pnpm exec vitest run src/app/front-door/team-sheet.test.tsx`

```text
 ❯ src/app/front-door/team-sheet.test.tsx (2 tests | 1 failed)
     × closes on a drag down on a change of team, and keeps the old team
AssertionError: expected [] to deeply equal [ 'close' ]
```

The old sheet is a hand-built panel, so a drag down on it never calls `onClose`. The hook runs the unit tests, so the loop and the fix are one commit.
Green: at `f31db328`, `cd apps/site && pnpm exec vitest run src/app/front-door/team-sheet.test.tsx`

```text
 Test Files  1 passed (1)
      Tests  2 passed (2)
```
Test verdict: PASS

## Comments

Closes with the squash merge of the PR of `win-team-sheet-swipe`. Commits: `0d840e00`, `f31db328`, `4711e416`, `3a39894b`. Date: 2026-11-16.
The test file `team-sheet.test.tsx` has 2 tests, and the loop went red at `0d840e00`, then green at `f31db328`.
The sheet now stays at the bottom edge on the tablet tier, where the old sheet sat at the center, so Brian checks it on a phone and a tablet.
AT-31 in `apps/site/src/app/page.test.tsx` failed in 3 of 4 hook runs, and it fails on `15a0f695` too, so it is the known flake of `main`.
Read 9 files: apps/site/src/app/front-door/team-sheet.tsx, packages/design/site/ui/sheet.tsx, packages/design/site/shell/menu-sheet.tsx, apps/site/src/ui-sdk-rule.test.ts, docs/agents/issue-tracker.md, GLOSSARY.md, .claude/plugin/skills/quick/format.md, .claude/plugin/skills/quick/judge.md, .claude/plugin/skills/implement/build.md.
