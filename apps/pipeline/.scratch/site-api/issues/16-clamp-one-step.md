# 16: Clamp the adjuster sum to one step

**What to build:** The chart ratio picks the start letter. The adjusters then move it by their summed steps, clamped to `CLAMP_STEPS` either way. With a clamp of two, a chart-even C start can end at A or F, so the adjusters outweigh the chart. Set the clamp to one so the chart weighs more and the adjusters tilt the letter by one at most.

**Why:** The commissioner's Chase trade on the week 7 chart: got 76.5, gave 72.5, ratio 1.055, a C start. Roster fit and trend each stepped down, and the page showed F against A on a trade the chart calls about even.

**Blocked by:** None (can start immediately).

**Status:** in-progress, branch `clamp-one-step`

- [ ] `CLAMP_STEPS = 1` in `src/cornerstone/tunables.py`, with the reason in the comment.
- [ ] The two clamp tests in `tests/test_rubric.py` expect a one-step move.
- [ ] The `HAND_WORKED` table of real week 6 trades carries the recomputed final letters and verdicts.
- [ ] `uv run pytest -q` passes with no failed test.
- [ ] Deploy needs Brian's `fly deploy`.
