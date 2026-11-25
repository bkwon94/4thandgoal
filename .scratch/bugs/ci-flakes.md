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
Cause: pending
Red: pending
Green: pending
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
