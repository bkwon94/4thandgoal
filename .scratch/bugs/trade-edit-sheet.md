# Edit a trade from its result

Kind: bug
Status: in-progress
Branch: `bug-trade-edit-sheet`.
Source: the session of 2026-11-18.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. Keep the trade result in place when Edit opens

Done condition: Edit opens a sheet with the current trade, where you can cancel or submit changes for a fresh grade.
Method: diagnosing-bugs
Cause: `edit` in `packages/analyzer/site/form/trade-form.tsx` reveals and scrolls the page Stack; `changeTrade` clears its result.

Red: at `8b6255f2` with `packages/analyzer/site/form/trade-form.test.tsx` of `9919e2d2`, `pnpm --dir apps/site test -- packages/analyzer/site/form/trade-form.test.tsx -t 'edits the captured trade'`

```text
TestingLibraryElementError: Unable to find an accessible element with the role "dialog" and name "Edit the trade"
Test Files  1 failed (1)
Tests  1 failed | 71 skipped (72)
```

Green: at `9919e2d2`, `pnpm --dir apps/site test -- packages/analyzer/site/form/trade-form.test.tsx -t 'edits the captured trade'`

```text
Test Files  1 passed (1)
Tests  1 passed | 71 skipped (72)
```

Test verdict: pending

## Comments

- The site hook includes the regression, so the loop and fix share commit `9919e2d2` under the documented fallback.
- A detached parent checkout reproduces the red result with the committed test file. That scratch worktree is removed.
- The regression uses captured API players and the existing HTTP test boundary; it adds no mock or runtime mode.
- The test checks prefill, result retention, Cancel, Close, Escape, focus return, nested player picks, and the changed request.
- `make check-fast BASE=main` exits 0 at `9919e2d2`: 138 root tests, 1,594 site tests, and 394 Python tests pass.
- One Python test is deselected by the existing fast check. The commit hook also passes.
