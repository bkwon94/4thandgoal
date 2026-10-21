# 04: Trend, injury, and handcuff adjusters

**What to build:** The breakdown gains three more adjusters. Trend and usage compares snap and target share over the last two weeks against the two before, with red-zone use as the tie break. Injury marks a got player who is out with no near return or who was on the report in three or more weeks. Handcuff treats a backup to the roster's own starting running back as insurance: he counts as 0 in the sums, and the fit and trend adjusters cannot step down because of him.

**Blocked by:** 02 (Schedules, depth charts, and points allowed per position), 03 (Fit and standing adjusters)

**Status:** done

- [x] Trend: got players up and gave players down is a step up. The reverse is a step down. Mixed is no step. Red-zone use breaks a tie inside the adjuster. The shares come from the history helpers.
- [x] Injury: a got player listed Out or on IR now with no return within two weeks, or on the report in three or more weeks this season, is a step down. It never fires for a player the standing adjuster credited as a return bet.
- [x] Handcuff: a got player who is second or lower on the depth chart of the NFL team whose starter is on the same fantasy roster. He counts as 0 in the trade value sums. A handcuff with no chart row keeps the start letter. The fit and trend adjusters cannot step down because of him.
- [x] When the depth chart is missing from the snapshot, the handcuff adjuster does not fire and the breakdown notes the source was missing.
- [x] The injury week count, the return window, and the share windows join the tunable table. The rubric file gains a section per adjuster.
- [x] Tests at the grade seam: trend up, trend down, mixed, red-zone tie break; injury down, injury at the cap, the return-bet exemption; handcuff with a chart row, handcuff with no chart row, the fit block, the missing depth chart note.
- [x] `uv run pytest -q` passes with no failed test.
