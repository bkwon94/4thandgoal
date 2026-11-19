# Past weeks in the menu sheet

Kind: bug
Status: in-progress
Branch: `bug-past-weeks-menu`.
Source: the session of 2026-11-19.
Boundary: holds. 2 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. Past weeks lists the newest week

Done condition: The "Past weeks" list of the menu sheet holds each published week except the newest one, and the "Past weeks" button does not show when no older week exists.
Method: diagnosing-bugs
Cause: `MenuSheet` in `packages/design/site/shell/menu-sheet.tsx` passes all of `weeks` to `PastWeeks`, newest first, so the list repeats the newest week of the week row, and the button shows with one published week.
Red: at `f2669872` with `packages/design/site/shell/top-band.test.tsx` of `5d27ac80`, `builtin cd apps/site && pnpm exec vitest run ../../packages/design/site/shell/top-band.test.tsx`

```text
 FAIL  ../../packages/design/site/shell/top-band.test.tsx > The top band has no week chip (AT-11) > keeps the week row and Past weeks in the menu sheet
AssertionError: expected [ [ 'WK 08', '/2026/week-08/' ], …(2) ] to deeply equal [ [ 'WK 07', '/2026/week-07/' ], …(1) ]
+     "WK 08",
 FAIL  ../../packages/design/site/shell/top-band.test.tsx > The menu sheet and the top band of the front door (AT-45, AT-47) > opens the latest report from the week row, and lists each older week under Past weeks
AssertionError: expected [ [ 'WK 08', '/2026/week-08/' ], …(2) ] to deeply equal [ [ 'WK 07', '/2026/week-07/' ], …(1) ]
 FAIL  ../../packages/design/site/shell/top-band.test.tsx > The menu sheet and the top band of the front door (AT-45, AT-47) > shows no Past weeks when the newest week is the one published week
AssertionError: expected <button type="button" …(3)>…(1)</button> to be null
 Test Files  1 failed (1)
      Tests  3 failed | 29 passed (32)
```

Green: at `5d27ac80`, `builtin cd apps/site && pnpm exec vitest run ../../packages/design/site/shell/top-band.test.tsx`

```text
 Test Files  1 passed (1)
      Tests  32 passed (32)
```

Test verdict: pending

### 2. The top edge of the menu sheet jumps when Past weeks opens

Done condition: When "Past weeks" opens or closes, the top edge of the menu sheet stays still, and only the list of weeks grows or shrinks under the button.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Comments
