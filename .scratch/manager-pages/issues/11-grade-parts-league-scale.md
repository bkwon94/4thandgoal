# 11: Two grade parts are not league-relative

**What to build:** the `GRADE_BANDS` comment says each part puts the league's worst roster at 0 and its best at 1. In `_RosterRead.parts`, `depth` is absolute: holes and the depth ratio, and it runs 0.61 to 1.00 on week 7. Half of `projection` is absolute: the mean `_place` against the line. So the week 7 median score is 58, a B, not a C, and the letters read 3 A, 4 B, 1 C, 4 D. Either put both parts on the league scale, or fix the comment and the bands. Needs Brian's decision. Pipeline repo.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Brian decides: league scale for both parts, or a fixed comment and fixed bands.
- [ ] The code, the `GRADE_BANDS` comment, and the tests agree on the scale of each part.
- [ ] The week 7 letters are checked against the decision.
- [ ] Every existing test passes. `ruff` is clean.
