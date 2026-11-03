# 20: Trend reasons with numbers

**What to build:** The trend adjuster reason names each traded player whose share moved, with the numbers: "Chase: target share 15%, down, over weeks 4 and 5." The number check in the analysis allows these numbers in the prose, the way the breakdown text is allowed today. The lead sentence stays as it is when the sides mix.

**Why:** The commissioner saw "the players it gets lose snap or target share" with no numbers and could not tell how it was computed.

**Blocked by:** 11 (both touch the number check in `src/cornerstone/analysis.py`).

**Status:** done

- [x] `_trend_step` in `src/cornerstone/adjusters.py` adds one clause per traded player with a share direction of up or down: the player's last name, the share kind, the percent, the direction, and the weeks behind each percent from `UsageShare.weeks_used`, as a list such as "weeks 4 and 5".
- [x] Players with flat shares or no data get no clause. A handcuff or a due-back player keeps the note it has today.
- [x] The breakdown text already feeds the allowed numbers in `_allowed`; check that the new numbers pass the check and add a test.
- [x] The decision page, site ticket 04, carries the reason in a reasoning row and passed its 390 check.
- [x] Tests on the saved week 6 snapshot: the Chase trade reason names Chase with target share 15% down. The fixture gives 19% over weeks 4 and 5, so the test asserts 19%.
- [x] `uv run pytest -q` passes with no failed test.
- [x] Deployed 2026-10-22.
