# Each sheet is the shared Sheet

Kind: quick-win
Status: in-progress
Branch: `win-one-sheet`.
Source: the session of 2026-11-16.
Boundary: holds. 4 items of one kind; no new term or ADR; no moved seam, each item swaps a part for the shared `Sheet` of `packages/design/site/ui/sheet.tsx`; each done condition is one sentence.

## Items

### 1. The sheet of the analyzer is the shared Sheet

Done condition: `packages/analyzer/site/form/sheet.tsx` renders the shared `Sheet` of `@cpc/design/ui/sheet` in place of the `Dialog`, so the player sheet and the team sheet of the analyzer drag closed like the team sheet of the front door.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

### 2. The claim sheet of the egg hunt is the shared Sheet

Done condition: `packages/eggs/site/hunt/claim-sheet.tsx` renders the shared `Sheet` of `@cpc/design/ui/sheet` in place of its own fixed `div` with `role="dialog"`, so it drags closed like the team sheet of the front door.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

### 3. The passphrase sheet of the front door is the shared Sheet

Done condition: `apps/site/src/app/front-door/passphrase-sheet.tsx` renders the shared `Sheet` of `@cpc/design/ui/sheet` in place of its own `motion.div` modal, and its field still stays above the keyboard.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

### 4. The passphrase dialog of the analyzer is the shared Sheet

Done condition: `packages/analyzer/site/form/passphrase-dialog.tsx` renders the shared `Sheet` of `@cpc/design/ui/sheet` in place of the centered `Dialog`, so the analyzer asks for the passphrase in the same sheet as the front door.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

## Comments
