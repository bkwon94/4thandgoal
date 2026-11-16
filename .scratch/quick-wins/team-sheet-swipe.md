# The team sheet closes on a swipe down

Kind: quick-win
Status: in-progress
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
