# Past weeks in the menu sheet

Kind: bug
Status: done
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

Test verdict: PASS

### 2. The top edge of the menu sheet jumps when Past weeks opens

Done condition: When "Past weeks" opens or closes, the top edge of the menu sheet stays still, and only the list of weeks grows or shrinks under the button.
Method: diagnosing-bugs
Cause: the ui-sdk Drawer under `Sheet` in `packages/design/site/ui/sheet.tsx` observes the size of the sheet, and on each resize springs it to the new height with a `translate` animation from minus the growth back to `0`. On the `side="top"` sheet of `MenuSheet` in `packages/design/site/shell/menu-sheet.tsx`, that spring moves the top edge up by about 62 px and back while the grid rows of `menu-past` grow or shrink.
Red: at `63493e53`, after `CLIENT=cpc pnpm build` in `apps/site`, `builtin cd apps/site && pnpm exec playwright test --project=floor e2e/menu-sheet.spec.ts`

```text
  ✘  1 [floor] › e2e/menu-sheet.spec.ts:36:5 › the top edge of the menu sheet stays still while Past weeks opens and closes (2.8s)
    Error: the top edge of the menu sheet moves 62.48410415649414px as Past weeks opens
    Expected: <= 1
    Received:    62.48410415649414
  1 failed
```

Green: at `373a596c`, after `CLIENT=cpc pnpm build` in `apps/site`, `builtin cd apps/site && pnpm exec playwright test --project=floor e2e/menu-sheet.spec.ts`

```text
  ✓  1 [floor] › e2e/menu-sheet.spec.ts:36:5 › the top edge of the menu sheet stays still while Past weeks opens and closes (2.5s)
  1 passed (3.0s)
```

Test verdict: PASS

## Comments

Closes with the squash merge of the PR of `bug-past-weeks-menu`. Commits: `5d27ac80`, `63493e53`, `373a596c`. Date: 2026-11-19.
Item 1 went red with 3 failed of 32 in `top-band.test.tsx`, then green with 32 of 32; item 2 went red at 62 px in `e2e/menu-sheet.spec.ts`, then green; `make check-fast BASE=main` passed with 486 of 486 site tests.
The fix of item 2 calls `finish()` on the `translate` animation of the ui-sdk Drawer, an internal detail, so a later ui-sdk version can break it, and the floor spec then goes red.
Nobody checked item 2 on a real iPhone in Safari yet.
Read 9 files: AGENTS.md, docs/agents/issue-tracker.md, docs/adr/0033-a-quick-run-skips-the-spec-flow.md, GLOSSARY.md, packages/design/site/shell/menu-sheet.tsx, packages/design/site/shell/top-band.test.tsx, packages/design/site/ui/sheet.tsx, apps/site/src/app/globals.css, apps/site/playwright.config.ts.
