# The rerun check reads no Bun failure, and the closed Deadline banner is under the tap floor

Kind: bug
Status: in-progress
Branch: `bug-rerun-and-banner`.
Source: the session of 2026-11-24, from the CI run of PR #93.
Boundary: holds. 2 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The rerun check finds no failure line in Bun output

Done condition: `scripts/rerun.py` reads the Bun lines `(fail) <test name>` and `error: expect(received).toBe(expected)` in a Red block as failure lines, so a quick file with a Bun loop gets no "the Red block quotes no failure line" problem.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

### 2. The Deadline banner after the Lock is 43 px tall

Done condition: After the Lock of cpc, the Deadline banner button is at least 44 px tall at 1280 px and at 1024 px, so the tap floor of `e2e/floor.spec.ts` passes on `/2026/managers/` and `/analyze/`.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Smoke

Smoke: pending

## Comments
