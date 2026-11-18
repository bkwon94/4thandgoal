# The Grade the Trade button shows no change while a grade runs

Kind: bug
Status: done
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
Test verdict: PASS

## Comments

Closes with the squash merge of the PR of `bug-grade-button-pending`. Commits: `ab08eb03`, `aee26144`, `7f484a57`, `0c9d03fe`. Date: 2026-11-17.
`make check-fast BASE=main` passes with 1594 site tests in 161 files and 138 root script tests, and the loop of item 1 went red at `ab08eb03`, then green at `aee26144`.
The accessible name of the button is "Grading…" during a grade, and the pending announcement "Grading the trade" stays.
Read 6 files: AGENTS.md, packages/analyzer/site/form/grade-bar.tsx, packages/design/site/ui/pending-button.tsx, packages/analyzer/site/form/trade-form.test.tsx, .claude/plugin/skills/quick/format.md, .claude/plugin/skills/quick/judge.md.
