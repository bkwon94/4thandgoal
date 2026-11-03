# 07: The Claude call

**What to build:** The analyze command without the skip flag prints an analysis paragraph per side, a final letter per side, and a verdict with one reason, all from one Claude call. The call reads the rubric, both breakdowns, and a fact sheet built from the grade input builders the weekly build no longer uses. Claude's final letter may differ from the code's by one step at most, with a stated reason. A letter further off is a parse failure that retries once and then falls back to the code's letters and verdict.

**Blocked by:** 05 (Schedule, clamp, and verdict)

**Status:** done

- [x] A fact sheet builder takes the proposed trade and the snapshot and returns facts with ids: points per game, position rank, usage, injury, team record and standing, roster need, and the trade values of the traded players only.
- [x] The call sends the rubric file, both breakdowns, and the fact sheet to the writer's model, through the same client and parse path as the writer. The call takes a callable so tests run with no Claude.
- [x] Structured output per side: a final letter, a one-line reason when it differs from the code's letter, and an analysis of three to five sentences with cited fact ids. A verdict with one reason, and a flag when it differs from the code's default.
- [x] A final letter more than one step from the code's letter is a parse failure. The call retries once. After a second failure the code's letters and verdict stand and each analysis reads "Analysis unavailable".
- [x] The number check from the verifier runs on the prose: every number must appear in a cited fact or the breakdown. A chart value, sum, or ratio in the prose fails the check and counts as a parse failure.
- [x] No chart value, chart name, or tier appears in the prose or the result.
- [x] `cornerstone analyze` without the skip flag prints the analysis per side, the letters, and the verdict.
- [x] Tests with the call patched: a good response passes through; a letter one step off passes with its reason; a letter two steps off retries and falls back; a chart value in the prose fails; a verdict flag is set when it differs from the code's.
- [x] `uv run pytest -q` passes with no failed test.
