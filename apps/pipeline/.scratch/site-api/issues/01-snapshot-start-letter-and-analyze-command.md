# 01: Snapshot, start letter, and the analyze command

**What to build:** A commissioner runs `cornerstone analyze` from the terminal with a season, two roster ids, the player ids each side gives, the asker's roster id, and a flag that skips the Claude call. The command grades the trade from a saved snapshot and prints a breakdown per side. In this ticket the breakdown holds the start letter only, with the consolidation and unlisted rules applied. The week 6 raw data and the week 6 chart values fixture form the snapshot, so no network is needed.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] A proposed trade model holds the season, two roster ids, the player ids each side gives, and the asker's roster id. Two sides only, players only.
- [x] A snapshot model holds what the grade reads: rosters, users, standings, the league's roster slots, the chart values for the chart week, season stats through the last completed week, and the as-of stamps. The fields for usage, injuries, schedules, depth charts, and points allowed exist and may be empty until ticket 02 fills them.
- [x] A snapshot builder loads the week 6 raw data and the week 6 chart values fixture into the model with no network.
- [x] A given player who is not on the giving roster is an input error that names the offending player id.
- [x] A tunable table in code holds every number the rubric names. This ticket adds the start letter bands and the consolidation margin. Each number has a name and a one-line comment.
- [x] A rubric markdown file sits in the prompts directory. It states the start letter rule, the consolidation rule, and the unlisted rule in plain words, and points at the tunable table for the numbers. Later tickets add their sections.
- [x] The grade function takes a proposed trade and a snapshot and returns a breakdown per side with the start letter and the reason. It uses the ratio of trade value got over trade value gave, with the bands lower bound inclusive.
- [x] Consolidation: when one side gives one player and gets two or more, the depth side's sum is divided by the margin in both ratios. A three-for-two trade gets no discount.
- [x] Unlisted: when any traded player has no chart row, both sides start at C and the breakdown says so.
- [x] The breakdown and the printed output hold no trade value, sum, ratio, or chart name.
- [x] `cornerstone analyze` with the skip-Claude flag prints the breakdown per side as text.
- [x] Tests feed a proposed trade and a snapshot at the grade seam: one case per band, a consolidation case, a three-for-two case with no discount, an unlisted case, and the not-on-roster error.
- [x] The glossary terms for the analyzer already match. Do not change them.
- [x] `uv run pytest -q` passes with no failed test.
