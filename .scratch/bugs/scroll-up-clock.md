# The scroll-up test of a typed question fails for norcal on main

Kind: bug
Status: in-progress
Branch: `bug-scroll-up-clock`.
Source: the session of 2026-11-14. The check `Check` of the merge of #46 failed on `main`, run 43593394866.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; the done condition is one sentence.

## Items

### 1. The test of a typed question in a scrolled-up Thread times out for norcal

Done condition: `e2e/front-door-scroll-up.spec.ts` passes for both clients `cpc` and `norcal` on any day, not only on 2026-11-13, because each test gets the same Topics and Suggestions.
Method: diagnosing-bugs
Cause: `openTopic` in `apps/site/e2e/door-motion.ts` taps "More" while the panel of the last pick still plays its exit, and the pill drops about 150 ms later when `AnimatePresence` in `src/app/front-door/suggestions.tsx` removes that panel, so on a slow runner the pill moves under the press, the tap is lost, and the list "All Topics" never opens. The day is not the cause: the typed test passed for norcal at 21 pinned clocks, three hours on each day from 2026-11-08 to 2026-11-14, and the PR check passed on the same tree at 11:49 UTC on 2026-11-14, 30 minutes before the check on `main` failed.
Red: at `069f68cb`, in `apps/site` with `out/` built by `CLIENT=norcal pnpm build`, `CLIENT=norcal pnpm exec playwright test --project=floor e2e/front-door-scroll-up.spec.ts`

The loop makes the race fire on each run, not only on a slow CI runner. The red commit gives the tap of "More" in `openTopic` a 100 ms press, as a finger holds it, with `click({ delay: 100 })`. The press then spans the drop of the pill. The output is the CI failure of run 43593394866, line for line. The typed test failed on each of 2 runs. The chip test runs the same `scrollUp`, and it failed in 1 of the 2 runs.

```text
  ✘  1 [floor] › e2e/front-door-scroll-up.spec.ts:70:5 › a question typed in a scrolled-up Thread scrolls to the top under the Thread header (30.0s)
    Error: locator.click: Test timeout of 30000ms exceeded.
      - waiting for getByRole('list', { name: 'All Topics' }).getByRole('button', { name: /^Your season:/ })
       at door-motion.ts:22
  1 failed
  1 passed (30.5s)
```

Green: at `93fe39b6`, in `apps/site` with `out/` built by `CLIENT=norcal pnpm build`, `CLIENT=norcal pnpm exec playwright test --project=floor e2e/front-door-scroll-up.spec.ts`

The fix makes `openTopic` wait until the list "All Topics" has left, so the pill stands still under the 100 ms press. The typed test also pins the same Friday as the chip test, so both tests get the same Suggestions. The same spec passes for `cpc` after `CLIENT=cpc pnpm build`: 2 passed. `e2e/front-door-scroll.spec.ts` also calls `openTopic`, and it passes for both clients.

```text
Running 2 tests using 2 workers
  ✓  1 [floor] › e2e/front-door-scroll-up.spec.ts:56:5 › a Suggestion chip tapped in a scrolled-up Thread scrolls its question to the top under the Thread header (8.3s)
  ✓  2 [floor] › e2e/front-door-scroll-up.spec.ts:70:5 › a question typed in a scrolled-up Thread scrolls to the top under the Thread header (8.5s)
  2 passed (9.1s)
```
Test verdict: PASS

## Comments
