# A tap on a result tile stays on its week

Kind: quick-win
Status: done
Branch: `win-stay-on-week`.
Source: the session of 2026-11-19.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. A tap on a result tile stays on its week

Done condition: On the season sim page, a tap on a result tile of a week sets that result and keeps that same week open, with no automatic open of the next week.
Method: tdd
Red: at `be23082e` with `packages/sim/site/page/sim-page.test.tsx` of `c8c63455`, `cd apps/site && pnpm exec vitest run ../../packages/sim/site/page/sim-page.test.tsx -t "stays on its week"`

```text
AssertionError: expected null to be 'page'
- Expected: "page"
+ Received: null
 ❯ sim-page.test.tsx:211:60  expect(weekItem("Wk 11").getAttribute("aria-current")).toBe("page")
 Tests  1 failed | 18 skipped (19)
```
Green: at `c8c63455`, `cd apps/site && pnpm exec vitest run ../../packages/sim/site/page/sim-page.test.tsx -t "stays on its week"`

```text
 Test Files  1 passed (1)
      Tests  1 passed | 18 skipped (19)
```
Test verdict: PASS

## Comments

Closes with the squash merge of the PR of `win-stay-on-week`. Commits: `be23082e`, `c8c63455`, `9923774b`. Date: 2026-11-19.
The loop of item 1 went red on the old code and green at the fix commit; `make check-fast BASE=main` passed with 47 site tests and 78 sim tests.
PRD line 168 and decision 04 of `season-sim` still describe the open of the next week; a later edit can bring them in line.
Read 6 files: packages/sim/site/page/sim-page.tsx, packages/sim/site/page/sim-page.test.tsx, packages/sim/site/page/week-page.tsx, .scratch/season-sim/PRD.md, .scratch/season-sim/decisions/04-prototype-the-sim-page.md, .claude/plugin/skills/quick/format.md.
