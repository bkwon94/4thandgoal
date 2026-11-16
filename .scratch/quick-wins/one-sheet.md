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
Red: at `4ca8b2d1` with `packages/analyzer/site/form/sheet.test.tsx` of `2b717bea`, `cd apps/site && npx vitest run ../../packages/analyzer/site/form/sheet.test.tsx`

```text
 FAIL  ../../packages/analyzer/site/form/sheet.test.tsx > the sheet of the analyzer > shows the grip of the shared Sheet, the title, the body, and the footer
AssertionError: expected null to be truthy
 FAIL  ../../packages/analyzer/site/form/sheet.test.tsx > the sheet of the analyzer > closes on a drag down and calls onClose
AssertionError: expected [] to deeply equal [ 'close' ]
 Test Files  1 failed (1)
      Tests  2 failed (2)
```

Green: at `2b717bea`, `cd apps/site && npx vitest run ../../packages/analyzer/site/form/sheet.test.tsx`

```text
 Test Files  1 passed (1)
      Tests  2 passed (2)
```
Test verdict: pending

### 2. The claim sheet of the egg hunt is the shared Sheet

Done condition: `packages/eggs/site/hunt/claim-sheet.tsx` renders the shared `Sheet` of `@cpc/design/ui/sheet` in place of its own fixed `div` with `role="dialog"`, so it drags closed like the team sheet of the front door.
Method: tdd
Red: at `4ccf87cd` with `packages/eggs/site/hunt/claim-sheet.test.tsx` of `1f96b744`, `cd apps/site && npx vitest run ../../packages/eggs/site/hunt/claim-sheet.test.tsx`

```text
 FAIL  ../../packages/eggs/site/hunt/claim-sheet.test.tsx > the claim sheet of the egg hunt > shows the grip of the shared Sheet and the team pills
AssertionError: expected null to be truthy
 FAIL  ../../packages/eggs/site/hunt/claim-sheet.test.tsx > the claim sheet of the egg hunt > closes on a drag down and calls onClose once
AssertionError: expected [] to deeply equal [ 'close' ]
 Test Files  1 failed (1)
      Tests  2 failed (2)
```

Green: at `1f96b744`, `cd apps/site && npx vitest run ../../packages/eggs/site/hunt/claim-sheet.test.tsx`

```text
 Test Files  1 passed (1)
      Tests  2 passed (2)
```
Test verdict: pending

### 3. The passphrase sheet of the front door is the shared Sheet

Done condition: `apps/site/src/app/front-door/passphrase-sheet.tsx` renders the shared `Sheet` of `@cpc/design/ui/sheet` in place of its own `motion.div` modal, and its field still stays above the keyboard.
Method: tdd
Red: at `6b576def~1` with `apps/site/src/app/front-door/passphrase-sheet.test.tsx` of `6b576def`, `cd apps/site && npx vitest run src/app/front-door/passphrase-sheet.test.tsx`

```text
 FAIL  src/app/front-door/passphrase-sheet.test.tsx > the passphrase sheet of the front door > shows the grip of the shared Sheet and keeps the focus in the field
AssertionError: expected null to be truthy
 FAIL  src/app/front-door/passphrase-sheet.test.tsx > the passphrase sheet of the front door > lifts the content by the keyboard signal so the field sits above the keyboard
AssertionError: expected '' to be 'var(--spacing-door-foot)' // Object.is equality
 FAIL  src/app/front-door/passphrase-sheet.test.tsx > the passphrase sheet of the front door > closes on a drag down and calls onClose once
AssertionError: expected [] to deeply equal [ 'close' ]
 Test Files  1 failed (1)
      Tests  3 failed | 3 passed (6)
```

Green: at `6b576def`, `cd apps/site && npx vitest run src/app/front-door/passphrase-sheet.test.tsx`

```text
 Test Files  1 passed (1)
      Tests  6 passed (6)
```
Test verdict: pending

### 4. The passphrase dialog of the analyzer is the shared Sheet

Done condition: `packages/analyzer/site/form/passphrase-dialog.tsx` renders the shared `Sheet` of `@cpc/design/ui/sheet` in place of the centered `Dialog`, so the analyzer asks for the passphrase in the same sheet as the front door.
Method: tdd
Red: at `7766f282` with `packages/analyzer/site/form/passphrase-dialog.test.tsx` of `60af5c88`, `cd apps/site && npx vitest run ../../packages/analyzer/site/form/passphrase-dialog.test.tsx`

```text
 FAIL  ../../packages/analyzer/site/form/passphrase-dialog.test.tsx > the passphrase dialog of the analyzer > renders the shared Sheet from the bottom, with no grip because it does not drag
AssertionError: expected null to be 'bottom' // Object.is equality
 Test Files  1 failed (1)
      Tests  1 failed | 2 passed (3)
```

Green: at `60af5c88`, `cd apps/site && npx vitest run ../../packages/analyzer/site/form/passphrase-dialog.test.tsx`

```text
 Test Files  1 passed (1)
      Tests  3 passed (3)
```
Test verdict: pending

## Comments
