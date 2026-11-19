# The rerun check misses a quoted Red line in colored output

Kind: bug
Status: in-progress
Branch: `bug-rerun-ansi`.
Source: the session of 2026-11-19, split out of the quick run `bug-season-sim-label`.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The rerun check misses a quoted Red line in colored output

Done condition: The rerun check in `scripts/rerun.py` matches a quoted Red line when the output of the loop holds ANSI color codes, as Vitest prints them on GitHub Actions.
Method: diagnosing-bugs
Cause: `normal` in `scripts/rerun.py` keeps the ANSI color codes of the loop output, so `shows` cannot find a quoted Red line inside the colored line that Vitest prints on GitHub Actions.
Red: at `1f21cc8e` with `scripts/test_rerun.py` of `244d7633`, `python3 -B -m unittest scripts.test_rerun.TheRerun.test_a_quoted_line_matches_output_with_ansi_color_codes`

```text
AssertionError: 1 != 0 : quick file: .scratch/bugs/add.md
  Red at 497471da: exit 1
FAIL item 1 (add gives the sum): the Red output has no line `Test Files  1 failed (1)`
Ran 1 test in 0.343s
FAILED (failures=1)
```

Green: at `244d7633`, `python3 -B -m unittest scripts.test_rerun.TheRerun.test_a_quoted_line_matches_output_with_ansi_color_codes`

```text
Ran 1 test in 0.300s
OK
```
Test verdict: pending

## Smoke

Smoke: none, no site or API change.

## Comments

The item moves here from PR 78, because the job `Run the loops of the quick file again` reads `scripts/rerun.py` from `main`, so a PR cannot fix the check that judges it.
