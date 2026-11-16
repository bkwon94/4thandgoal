# The Trade Analyzer is in the menu with the front door on

Kind: quick-win
Status: in-progress
Branch: `win-analyzer-in-menu`.
Source: the session of 2026-11-15.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam, because `front_door_items` keeps its shape and only gains an item; each done condition is one sentence.

## Items

### 1. The menu of cpc and norcal lists the Trade Analyzer

Done condition: For cpc and norcal with the front door on, the menu lists Home, the week, Power Rankings, Managers, and Trade Analyzer in that order, so the menu sheet and the desktop pill bar each link to the Trade Analyzer.
Method: tdd
Red: at `a98facb0` with `apps/site/src/app/shell-props.test.ts` of `dd7fbc4a`, `cd apps/site && CLIENT=cpc node scripts/client-build.mjs && pnpm exec vitest run src/app/shell-props.test.ts`

```text
 FAIL  src/app/shell-props.test.ts > shellProps of cpc > keeps the items and the labels of the CPC menu ...
AssertionError: expected [ 'Home', 'Week 8', ...(2) ] to deeply equal [ 'Home', 'Week 8', ...(3) ]
    "Managers",
-   "Trade Analyzer",
 FAIL  ... the menu keeps its five items
AssertionError: expected [ <a href="/" ...>, ...(3) ] to have a length of 5 but got 4
 Tests  2 failed | 14 passed (16)
```

The hook runs the unit tests, so a red commit fails the hook. The loop and the fix sit in one commit.
Green: at `dd7fbc4a`, `cd apps/site && CLIENT=cpc node scripts/client-build.mjs && pnpm exec vitest run src/app/shell-props.test.ts`

```text
 Test Files  1 passed (1)
      Tests  16 passed (16)
```
Test verdict: pending

## Comments
