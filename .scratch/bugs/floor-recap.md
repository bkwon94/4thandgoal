# The week 10 floor test fails on main after the tap on recap 3

Kind: bug
Status: in-progress
Branch: `bug-floor-recap`.
Source: the session of 2026-11-19. Main Check run 44611529354 at `ac287f48` and PRs #80 and #81 fail it.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The floor of cpc /2026/week-10/ fails after the tap on recap 3 at 1280px

Done condition: The full floor test of cpc `/2026/week-10/` after the tap on `recap-3` passes at 1280px in dark and light, and the floor still fails on a real contrast fault.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Smoke

Smoke: pending

## Comments

- CI error: "incomplete: .max-rail\:sr-only Fix any of the following: Element's background color could not be determined because it partially overlaps other elements". It first shows on main at `ac287f48` (#78); main at `fd05189c` and `8780eefb` failed on other tests.
