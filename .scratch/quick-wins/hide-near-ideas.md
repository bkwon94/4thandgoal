# The trade ideas show only real offers

Kind: quick-win
Status: done
Branch: `win-hide-near-ideas`.
Source: the session of 2026-11-13.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The trade ideas Answer hides the near ideas

Done condition: the trade ideas Answer of the front door shows no near idea, so neither the "Also weighed" list under real offers nor the "Ideas, none a clear win" list shows, and a search with no offer shows its plain empty line and the Trade page link.
Method: tdd
Red: at `dde28f55` with `apps/site/src/app/page-trade.test.tsx` of `23471f01`, `cd apps/site && pnpm exec vitest run src/app/page-trade.test.tsx -t "near ideas"`

```text
 × hides the near ideas and shows the plain empty line and the Trade page link when no offer stands
 × hides the near ideas under the real offers
AssertionError: expected <ul aria-labelledby="_r_10_" …(1)>…(2)</ul> to be null
AssertionError: expected <ul aria-labelledby="_r_24_" …(1)>…(1)</ul> to be null
 Tests  2 failed | 21 skipped (23)
```
Green: at `23471f01`, `cd apps/site && pnpm exec vitest run src/app/page-trade.test.tsx -t "near ideas"`

```text
 Test Files  1 passed (1)
      Tests  2 passed | 21 skipped (23)
```
Test verdict: PASS

## Comments
- Closes with the squash merge of the PR of `win-hide-near-ideas`. Commits: `23471f01`. Date: 2026-11-13.
- The full site suite has 1506 tests passed, the floor is green in cpc (158) and norcal (154), and the loop went red, then green.
- Notes for a later run: with no offer, the plain line can be `NO_CLEAR_PICK` in `packages/analyzer/python/src/analyzer/finder_pick.py:56`, which still says "these are ideas to weigh"; the judge model may write a line like it too.
- Read 4 files: apps/site/src/app/front-door/trade-answer.tsx, apps/site/src/app/page-trade.test.tsx, packages/analyzer/python/src/analyzer/finder_pick.py, .claude/plugin/skills/quick/judge.md.
