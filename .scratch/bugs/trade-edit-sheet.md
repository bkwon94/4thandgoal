# Edit a trade from its result

Kind: bug
Status: done
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

Test verdict: PASS

## Comments

- The site hook includes the regression, so the loop and fix share commit `9919e2d2` under the documented fallback.
- A detached parent checkout reproduces the red result with the committed test file. That scratch worktree is removed.
- The regression uses captured API players and the existing HTTP test boundary; it adds no mock or runtime mode.
- The test checks prefill, result retention, Cancel, Close, Escape, focus return, nested player picks, and the changed request.
- `make check-fast BASE=main` exits 0 at `9919e2d2`: 138 root tests, 1,594 site tests, and 394 Python tests pass.
- One Python test is deselected by the existing fast check. The commit hook also passes.

- Closes with the squash merge of the PR of `bug-trade-edit-sheet`. Commits: `8b6255f2`, `9919e2d2`, `34c0832c`, `f5e87d0f`, `dac5775c`. Date: 2026-11-18.
- The regression goes red, then green. The fix fast check passes 2,126 tests.
- Phone and desktop browser checks each grade a live trade, cancel an edit, then submit a changed trade.
- Read 32 files: AGENTS.md, apps/site/AGENTS.md, .scratch/bugs/trade-edit-sheet.md, .claude/plugin/skills/quick/SKILL.md, .claude/plugin/skills/quick/format.md, .claude/plugin/skills/quick/judge.md, .claude/plugin/skills/implement/build.md, docs/agents/state.md, docs/agents/issue-tracker.md, GLOSSARY.md, docs/adr/0015-a-port-has-one-fake.md, docs/adr/0033-a-quick-run-skips-the-spec-flow.md, docs/adr/0034-a-sheet-you-can-drag-follows-a-spring.md, packages/analyzer/site/form/trade-form.tsx, packages/analyzer/site/form/trade-form.test.tsx, packages/analyzer/site/form/form-steps.ts, packages/analyzer/site/form/sheet.tsx, packages/analyzer/site/form/sheet.test.tsx, packages/analyzer/site/form/player-sheet.tsx, packages/analyzer/site/form/grade-bar.tsx, packages/analyzer/site/form/use-request.ts, packages/analyzer/site/lib/fixtures/api.ts, packages/analyzer/site/lib/fixtures/analyze-response.json, packages/analyzer/site/lib/fixtures/analyze-response-trade-a.json, packages/design/site/ui/sheet.tsx, packages/design/site/ui/sheet-jsdom.ts, apps/site/vitest.config.mts, apps/site/package.json, apps/site/src/fixtures/raw-teams.ts, apps/site/src/app/_routes/analyzer/idle-stage.test.tsx, Makefile, .pre-commit-config.yaml.
