# 03: The trade card with no grade

**What to build:** The trade card shows the two sides, the player rows with headshots, and the recap text under the rows. No letter, no "No grade", no toggle. A chapter whose writer call failed shows the sides sentence as the recap. The page holds at 390 wide.

**Blocked by:** 02 (the recap chapter on the sheet and in the writer)

**Status:** ready-for-agent

- [ ] The card keeps the header, the two sides with team name and avatar, and the player rows with headshots and picks.
- [ ] The grade letter, the "No grade" fallback, the "Read the grade" button, and the hidden panel leave the template.
- [ ] The recap text sits under the rows and is always visible.
- [ ] A chapter with no blurb, or a fallback blurb, renders the sides sentence as the recap.
- [ ] The renderer's trade card builder no longer reads grades.
- [ ] The stylesheet drops the grade and the trade toggle rules. The matchup row toggle keeps working.
- [ ] The script no longer binds the trade card. The matchup rows still toggle.
- [ ] Render tests: the card holds the sides and the rows, no grade element, no button, and the recap text; a chapter with no blurb shows the sides sentence.
- [ ] The week 6 page renders from the saved data with no writer call and shows no horizontal scroll at 390 wide, checked with the browser tool, screenshots read by a person.
- [ ] `uv run pytest -q` passes with no failed test.
