# 03: The trade card with no grade

**What to build:** The trade card shows the two sides, the player rows with headshots, and the recap text under the rows. No letter, no "No grade", no toggle. A chapter whose writer call failed shows the sides sentence as the recap. The page holds at 390 wide.

**Blocked by:** 02 (the recap chapter on the sheet and in the writer)

**Status:** done

- [x] The card keeps the header, the two sides with team name and avatar, and the player rows with headshots and picks.
- [x] The grade letter, the "No grade" fallback, the "Read the grade" button, and the hidden panel leave the template.
- [x] The recap text sits under the rows and is always visible.
- [x] A chapter with no blurb, or a fallback blurb, renders the sides sentence as the recap.
- [x] The renderer's trade card builder no longer reads grades.
- [x] The stylesheet drops the grade and the trade toggle rules. The matchup row toggle keeps working.
- [x] The script no longer binds the trade card. The matchup rows still toggle.
- [x] Render tests: the card holds the sides and the rows, no grade element, no button, and the recap text; a chapter with no blurb shows the sides sentence.
- [x] The week 6 page renders from the saved data with no writer call and shows no horizontal scroll at 390 wide, checked with the browser tool, screenshots read by a person.
- [x] `uv run pytest -q` passes with no failed test.
