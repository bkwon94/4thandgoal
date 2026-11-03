# 16 — Build report

**Status:** DONE. Commit `0046ae6` on branch `nflverse-16`. Not pushed. Not merged.

## What changed

- `src/cornerstone/nflverse_expected.py` imports the shared helper `r2` from `cornerstone.models`.
- `read_expected` rounds each expected value with `r2`, not with `round(..., 2)`.
- `window_gap` rounds the mean gap with `r2`, not with `round(..., 2)`.
- `r2` uses `Decimal(str(x))` and `ROUND_HALF_UP`. The change adds no second helper.
- The file has no other `round(` calls.

## Files

1. `src/cornerstone/nflverse_expected.py`: 3 lines changed.
2. `tests/test_nflverse_expected.py`: 2 tests added.
3. `.scratch/nflverse/issues/16-the-expected-points-round-half-up.md`: 3 boxes ticked. Status stays `open`.

## Tests added

- `test_an_expected_value_on_a_half_cent_rounds_half_up`: a fixture row with an expected total of 16.805 gives 16.81.
- `test_a_window_gap_on_a_half_cent_rounds_half_up`: two gaps of 5.125 give a mean gap of 5.13.

Both tests failed first: 16.8 and 5.12 came back. Both pass after the change.

## Checks

- Command: `uv run pytest -q`
- Last line: `1038 passed, 9 deselected in 183.32s (0:03:03)`
- Ruff: `uv run ruff check --line-length 120 src tests` gives 135 errors before and 135 after. The two touched files have none.

## Concerns

None. The existing tests pass unchanged. `r2` rounds the `str` form of the float, so 16.805 rounds as the reader sees it.

# 16 — Fix round 1

**Status:** DONE. Commit `204cbdd` on branch `nflverse-16`. Not pushed. Not merged.

## What changed

- `_expected` does the rescale on `Decimal(str(...))` values and returns a `Decimal`. This follows the inline pattern in `facts_nflverse.py` and `facts_matchup.py`.
- `read_expected` rounds the result with `r2(float(...))`. A comment says why the math is exact.
- `window_gap` subtracts and sums the gaps on `Decimal(str(...))` values, then divides and rounds with `r2`.
- The change adds no helper. `_expected` has no other caller.

## Tests that cover the fix

1. `test_an_expected_value_on_a_half_cent_rounds_half_up` now runs the full rescale: 16.775 - 0.5 * 0.02 + 1 * 0.04 = 16.805. Float math gives 16.804999999999996. The test expects 16.81.
2. `test_a_half_ppr_rescale_on_a_half_cent_rounds_half_up` is new: the review row 8.44 - 0.5 * 2.65 gives 7.12.
3. `test_a_window_gap_with_float_drift_rounds_half_up` is new: the review window gives 1.97, not 1.96.

All three failed on the round 0 code and pass now.

## Checks

- `uv run pytest -q tests/test_nflverse_expected.py`: `18 passed in 0.09s`
- `uv run pytest -q`: `1040 passed, 9 deselected in 157.39s (0:02:37)`
- Ruff: 135 errors, the same as main.

## Concerns

None. I found no input that drifts under 16.805 with receptions alone. The 16.805 test adds an interception term to get the drift.
