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
Red: pending
Green: pending
Test verdict: pending

## Smoke

Smoke: none, no site or API change.

## Comments

The item moves here from PR 78, because the job `Run the loops of the quick file again` reads `scripts/rerun.py` from `main`, so a PR cannot fix the check that judges it.
