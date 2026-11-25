# Two flaky browser tests of the site check

Kind: bug
Status: in-progress
Branch: `bug-ci-flakes`.
Source: the session of 2026-11-25. Both tests turned the CI check `Check` red on PR #98.
Boundary: holds. 2 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The scene timing test fails when the scene settles a little early

Done condition: `e2e/scene.spec.ts` "settles in about 1.5 s" passes on each CI run where the scene settles within its designed time, with no retry and no wider bound than the cause needs.
Method: diagnosing-bugs.
Cause: the test "settles in about 1.5 s" in `apps/site/e2e/scene.spec.ts` reads the entry time when its MutationObserver callback runs. That callback runs only after the task of `enter()` in `packages/design/site/parts/scene-canvas.ts` ends, which includes the first `tick()` and its `draw()`. So a slow first frame on CI makes the time from entry to rest read under 1750 ms, while the clock of the scene reads 1750 ms or more. A local probe at a 60x CPU throttle gave an entry lag of 12 to 15 ms, a rest lag near 1 ms, and a measure of 1744 to 1745 ms, as on CI.
Red: at `ae6e61ce`, `CLIENT=cpc pnpm exec playwright test e2e/scene.spec.ts --project=floor-timing --workers=1 -g "settles in about 1.5 s" --repeat-each=5`

```text
cpc: the scene came to rest 1713 ms after entry
cpc: the scene came to rest 1680 ms after entry
cpc: the scene came to rest 1687 ms after entry
cpc: the scene came to rest 1719 ms after entry
    Error: expect(received).toBeGreaterThanOrEqual(expected)
    Expected: >= 1750
    Received:    1713
    Error: expect(received).toBeGreaterThanOrEqual(expected)
    Received:    1680
  5 failed
  5 passed (46.1s)
```

The 5 failed runs are the test "settles in about 1.5 s when the frame of the entry is slow". It throttles the CPU 200x through the Chrome DevTools Protocol for the re-entry of the hero only.

Green: at `3200d4f1`, `CLIENT=cpc pnpm exec playwright test e2e/scene.spec.ts --project=floor-timing --workers=1 -g "settles in about 1.5 s" --repeat-each=5`

```text
cpc: the scene came to rest 1755 ms after entry
  ✓   1 [floor-timing] › e2e/scene.spec.ts:339:7 › ... settles in about 1.5 s, and is not in the chart at 0.4 s (AT-16) @timing (2.4s)
cpc: the scene came to rest 1764 ms after entry
  ✓   2 [floor-timing] › e2e/scene.spec.ts:360:7 › ... settles in about 1.5 s when the frame of the entry is slow @timing (6.5s)
  10 passed (45.8s)
```

The fix writes the start time of each play to `data-scene-start`, and both tests measure from it. The floor of 1750 ms has no rounding now, because the entry and the rest read one clock. The fix commit also gives the poll of the slow-entry test gaps of 20 ms, so the throttle ends far before the rest. Without it, one run held the throttle late and read 1960 ms.
Test verdict: pending

### 2. The scrolled-up Thread test cannot find the "Your season" Topic on CI

Done condition: `e2e/front-door-scroll-up.spec.ts` "a question typed in a scrolled-up Thread" finds its Topic button on each run, with no retry and no longer timeout.
Method: diagnosing-bugs.
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Smoke

Smoke: pending

## Comments
