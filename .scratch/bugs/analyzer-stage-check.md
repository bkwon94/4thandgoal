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
Cause: pending
Red: pending
Green: pending
Test verdict: pending

### 2. The `site` job of the Check has a timeout of 15 minutes, too tight

Done condition: The `site` job of `.github/workflows/check.yml` has `timeout-minutes: 25`.
Method: text only
Red: pending
Green: pending
Test verdict: pending

## Comments
