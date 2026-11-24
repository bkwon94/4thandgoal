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
Cause: `FAILURE_MARK` in `scripts/rerun.py` reads only "FAIL", "Error", "✘", "×", "failed", and "E ", so `read_runs` finds no failure line in the Bun lines "(fail) <test name>" and "error: expect(...)".
Red: at `5292c3e3` with `scripts/test_rerun.py` of `efccfa32`, `python3 -B -m unittest discover -s scripts -p test_rerun.py -k bun`

```text
FAIL: test_the_bun_lines_of_a_failed_test_are_failure_lines (test_rerun.TheRerun.test_the_bun_lines_of_a_failed_test_are_failure_lines)
AssertionError: 1 != 0 : quick file: .scratch/bugs/add.md
item 1 (add gives the sum): does not hold
FAIL item 1 (add gives the sum): the Red block quotes no failure line
Ran 1 test in 0.182s
FAILED (failures=1)
```

Green: at `efccfa32`, `python3 -B -m unittest discover -s scripts -p test_rerun.py -k bun`

```text
Ran 1 test in 0.236s

OK
```
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
