# 16: Clamp the adjuster sum to one step

**What to build:** The chart ratio picks the start letter. The adjusters then move it by their summed steps, clamped to `CLAMP_STEPS` either way. With a clamp of two, a chart-even C start can end at A or F, so the adjusters outweigh the chart. Set the clamp to one so the chart weighs more and the adjusters tilt the letter by one at most.

**Why:** The commissioner's Chase trade on the week 7 chart: got 76.5, gave 72.5, ratio 1.055, a C start. Roster fit and trend each stepped down, and the page showed F against A on a trade the chart calls about even.

**Blocked by:** None (can start immediately).

**Status:** done

- [ ] `CLAMP_STEPS = 1` in `src/cornerstone/tunables.py`, with the reason in the comment.
- [ ] The two clamp tests in `tests/test_rubric.py` expect a one-step move.
- [ ] The `HAND_WORKED` table of real week 6 trades carries the recomputed final letters and verdicts.
- [ ] `uv run pytest -q` passes with no failed test.
- [ ] Deploy needs Brian's `fly deploy`.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in e164732c.
Proof: "Clamp the adjuster sum to one step" merged in da7ee83f on `main`; later manager brain c133eb89 removed the rubric and `CLAMP_STEPS`.
Read 1 file: .scratch/todoist-queue/audit.md.
