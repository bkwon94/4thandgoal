# The Check on main fails after the analyzer-stage merge

Kind: bug
Status: in-progress
Branch: `bug-analyzer-stage-check`.
Source: the handoff file `.handoff/analyzer-stage-deploy.md`.
Boundary: holds. 2 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The AT-5 "wait dips" e2e test is flaky on CI

Done condition: The test "wait dips" of `apps/site/e2e/analyzer-stage.spec.ts` passes under a CPU slowdown that makes the old test fail, and still fails if a side holds the weight much less than about 1.25 s in turn.
Method: diagnosing-bugs
Cause: the test "wait dips" in `apps/site/e2e/analyzer-stage.spec.ts` stamps the first sample of each dip after a 500 ms wait and a shot, so a slow shot on CI makes a turn of 1250 ms read short; the product turn `TURN_MS` in `packages/design/site/parts/mesh-math.ts` is 1250 ms. The fix samples the pulls on each frame in the page, with the clock of the page.
Red: at `3c1ee85d`, `cd apps/site && CLIENT=cpc pnpm exec playwright test --project=floor analyzer-stage.spec.ts -g "wait dips"`

```text
wait dips: cpc: side 0 1069-1069 ms, side 1 2251-2251 ms, side 0 3496-3496 ms, side 1 4678-4678 ms, side 0 5093-5093 ms
  ✘  1 [floor] › e2e/analyzer-stage.spec.ts:324:7 › the wait, with motion on › wait dips: cpc the mesh dips under each side in turn, about 1.25 s each, 1280px, 8x CPU slowdown (AT-5) (7.0s)
    Error: side 1 held the weight 415 ms
    Expected: > 1000
    Received:   415
  1 failed
```

Green: at `ec304519`, `cd apps/site && CLIENT=cpc pnpm exec playwright test --project=floor analyzer-stage.spec.ts -g "wait dips"`

```text
wait dips: cpc: side 0 -17-950 ms, side 1 1216-2200 ms, side 0 2483-3450 ms, side 1 3733-4699 ms, side 0 4966-5016 ms
  ✓  1 [floor] › e2e/analyzer-stage.spec.ts:324:7 › the wait, with motion on › wait dips: cpc the mesh dips under each side in turn, about 1.25 s each, 1280px, 8x CPU slowdown (AT-5) (7.0s)
  1 passed (7.6s)
```

A check at `ec304519` with `TURN_MS = 900` and no commit fails the same command: `side 1 held the weight 900 ms`, `Expected: > 1000`.
Test verdict: pending

### 2. The `site` job of the Check has a timeout of 15 minutes, too tight

Done condition: The `site` job of `.github/workflows/check.yml` has `timeout-minutes: 25`.
Method: text only
Red: pending
Green: pending
Test verdict: pending

## Comments
