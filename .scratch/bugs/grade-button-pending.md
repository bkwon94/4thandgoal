# The Grade the Trade button shows no change while a grade runs

Kind: bug
Status: in-progress
Branch: `bug-grade-button-pending`.
Source: the session of 2026-11-17.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The Grade the Trade button shows no change while a grade runs

Done condition: While `grading` is true, the button of `GradeBar` shows the label "Grading…" in the muted style of the off bar, and it shows "Grade the Trade" in the accent style again when `grading` is false.
Method: diagnosing-bugs
Cause: `GradeBar` in `packages/analyzer/site/form/grade-bar.tsx` gives the button one fixed label and the accent classes in every state, and its only pending style, `aria-disabled:cursor-progress`, tracks the press, so a grade shows no change on the button, and a grade that the Finder starts has no press at all.
Red: at `ab08eb03` with `packages/analyzer/site/form/grade-bar.test.tsx` of `aee26144`, `pnpm --dir apps/site exec vitest run packages/analyzer/site/form/grade-bar.test.tsx`

```text
 FAIL  ../../packages/analyzer/site/form/grade-bar.test.tsx > the grade bar > shows Grading… in the muted style while grading is true, and Grade the Trade in the accent style after
AssertionError: expected 'Grade the Trade' to be 'Grading…' // Object.is equality

Expected: "Grading…"
Received: "Grade the Trade"

 Test Files  1 failed (1)
      Tests  1 failed (1)
```

Green: at `aee26144`, `pnpm --dir apps/site exec vitest run packages/analyzer/site/form/grade-bar.test.tsx`

```text
 Test Files  1 passed (1)
      Tests  1 passed (1)
```
Test verdict: pending

## Comments
