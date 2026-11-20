# The wait contrast test of the analyzer stage fails on a slow runner

Kind: bug
Status: in-progress
Branch: `bug-analyzer-wait`.
Source: the handoff file `.handoff/flaky-specs.md`, item 5, and Check run 44645738360 of PR #80.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The wait hero of cpc breaks the readability floor on a loaded runner

Done condition: The AT-20 wait contrast test of `apps/site/e2e/analyzer-stage.spec.ts` passes when the frames of the wait come late, and it still fails when a hero text of the wait drops below 4.5:1.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Smoke

Smoke: pending

## Comments

- CI failure in run 44645738360: "the wait hero of cpc breaks the readability floor" in "wait contrast: cpc each hero text reaches 4.5:1 in 10 samples over 3 s of the wait, light 1280px (AT-20)". The handoff names the same spec at run 44201201184 and run 44393438643.
