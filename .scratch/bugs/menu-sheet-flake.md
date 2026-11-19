# The menu sheet spec fails when the motion starts late

Kind: bug
Status: in-progress
Branch: `bug-menu-sheet-flake`.
Source: the session of 2026-11-19, after the `Check` run 44585015323 on `main` failed in the "closes" step of `apps/site/e2e/menu-sheet.spec.ts`.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; the done condition is one sentence.

## Items

### 1. The menu sheet spec stops its samples before the list moves

Done condition: `apps/site/e2e/menu-sheet.spec.ts` passes when the motion of the list of weeks starts late after a tap on "Past weeks", and it still fails when the top edge of the menu sheet moves.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Comments
