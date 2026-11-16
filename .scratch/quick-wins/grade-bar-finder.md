# The grade bar keeps clear of the finder

Kind: quick-win
Status: in-progress
Branch: `win-grade-bar-finder`.
Source: the session of 2026-11-16.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam, it changes the position of one part and adds no port, page, or data shape; the done condition is one sentence.

## Items

### 1. The "Grade the Trade" bar stops at the end of the trade form

Done condition: On the analyzer page with the finder on, the "Grade the Trade" bar stays pinned at the bottom of the screen while the trade form is in view, and rests at the end of the form when the reader scrolls to the finder, so it covers no finder card.
Method: tdd
Red: at `7b186906`, `cd apps/site && pnpm check:grade-bar`

```text
  ✓  [grade-bar] › e2e/grade-bar.spec.ts:80:5 › the bar stays pinned at the bottom of the screen over the top of the form
  ✘  [grade-bar] › e2e/grade-bar.spec.ts:62:5 › the bar rests at the end of the form and covers no part of the finder (grade-bar-finder item 1)
    Error: the bar overlaps the part by 44px
    Expected: <= 0
    Received:    44
  1 failed
  1 passed
```
Green: at `6b43dfb1`, `cd apps/site && pnpm check:grade-bar`

```text
  ✓  [grade-bar] › e2e/grade-bar.spec.ts:80:5 › the bar stays pinned at the bottom of the screen over the top of the form
  ✓  [grade-bar] › e2e/grade-bar.spec.ts:62:5 › the bar rests at the end of the form and covers no part of the finder (grade-bar-finder item 1)
  2 passed
```
Test verdict: pending

## Comments

- The command `pnpm check:grade-bar` builds the export of norcal, the client with the finder on, then runs the Playwright project `grade-bar`.
