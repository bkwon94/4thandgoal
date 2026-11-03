# 16 — Spec review

**Verdict:** Not clean. One Important finding. The diff meets each ticked box literally. It does not meet the ticket aim, "a half rounds up every time", on real data.

## Checklist

1. "16.805 rounds to 16.81": met. `tests/test_nflverse_expected.py:50` feeds a row with a total of 16.805 and zero receptions.
2. "5.125 rounds to 5.13": met. `tests/test_nflverse_expected.py:114` gives two gaps of exactly 5.125.
3. "Existing tests pass unchanged": met. The diff edits no existing test. The builder reports `1038 passed`.

## The helper `r2`

`src/cornerstone/models.py:14-16` rounds `Decimal(str(x))` with `ROUND_HALF_UP`. `str(16.805)` is `'16.805'`, so `r2(16.805)` gives 16.81. `round(16.805, 2)` gives 16.8. The literal float input is safe.

## Real-data check

File: `data/cache/nflverse/ep_weekly_2026.csv` in the main repo. League scoring from `data/2026/week-06/raw/league.json`: `rec` 0.5, `pass_int` -1.0.

- Week 6: 288 rows. The old `round` and `r2` disagree on 46 rows. Example: Derrick Henry, 16.935, `round` 16.93, `r2` 16.94.
- Week 6: `r2` still gives a cent under the exact decimal half-up value on 21 rows. Example: Denzel Boston, 8.44 - 0.5 * 2.65 = 7.115 exact. The float sum is `7.114999999999999`, so `r2` gives 7.11. `round` gives 7.11 too.
- All weeks: 1991 rows, 292 disagreements, 145 rows still a cent low.

## Critical

None.

## Important

1. `src/cornerstone/nflverse_expected.py:37-39`: `_expected` adds and multiplies floats before `r2` rounds. The sum drifts under the half, and `str` keeps the drift. 21 of 288 week 6 rows still round down. Fix: do the rescale on `Decimal(str(...))` values, as `sub` in `models.py:19-21` does, then quantize.
2. `src/cornerstone/nflverse_expected.py:74,77`: `window_gap` subtracts and averages floats before `r2`. A random test of 20000 two-game windows gave 2939 cent-low results. Example: actual 4.0 and 25.4, expected 19.09 and 6.38, exact mean 1.965, result 1.96. Fix: sum the gaps on `Decimal(str(...))` values, then divide and quantize.

## Minor

1. `tests/test_nflverse_expected.py:50`: the test zeroes `receptions_exp`, so it never runs the rescale arithmetic. Fix: add a case with a half-PPR rescale, such as 8.44 and 2.65 receptions, that must give 7.12.

# 16 — Scoped re-review of `204cbdd`

**Verdict:** Clean. Both findings are ADDRESSED. The fix diff adds no new defect.

## Findings

1. Important, float drift before `r2`: ADDRESSED. `_expected` (`src/cornerstone/nflverse_expected.py:31-41`) does the rescale on `Decimal(str(...))` values. `window_gap` (`:79-82`) subtracts and sums on `Decimal`, then divides. `r2(float(...))` is safe, because the shortest `str` of the float keeps a half. A random test of 20000 windows of 2 or 3 games now gives 0 cent-low results, down from 2939.
2. Minor, the test skipped the rescale: ADDRESSED. The fixture columns are `receptions_exp, pass_interception_exp, total_fantasy_points_exp`. So `tests/test_nflverse_expected.py:55` sets 0.02 receptions, 0.04 interceptions, and 16.775 total. Two more tests cover the Denzel Boston row (7.12) and the drift window (1.97). `18 passed`.

## Real-data check

Week 6, 288 rows: 0 rows round a true half down.

One row differs from a Decimal read of the literal CSV text. Tyler Goodson's file total is `7.1899999999999995`, with 2.09 receptions. The exact sum is `6.1449999999999995`, so a literal read gives 6.14. `r2(float(...))` turns that sum into the float `6.145`, so the code gives 6.15. The file means 7.19, and 7.19 - 1.045 = 6.145, so 6.15 is the meant result. All weeks: 5 such rows, all with float noise in the CSV text.

## Minor

1. `src/cornerstone/nflverse_expected.py:65`: the code gets the meant value on noisy file text only because `float()` then `str()` collapses `6.1449999999999995` to `6.145`. The result is right, but the reason is not stated. Fix: none needed. Optionally add a one-line comment, or a test with the Goodson row that expects 6.15.
