# The trade ideas show only real offers

Kind: quick-win
Status: in-progress
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
Test verdict: pending

## Comments
