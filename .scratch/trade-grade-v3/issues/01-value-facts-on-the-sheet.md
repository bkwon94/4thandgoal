# 01: Value facts on the sheet

**What to build:** A trade chapter carries a trade value for each traded player and a value sum for each side, from chart values handed to the bundle builder. The writer sees them on the fact sheet. Nothing on the page changes in this ticket.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] The bundle builder takes an optional chart values input beside the nflverse week. Without it, the sheet is the v2 sheet.
- [ ] A chart values model holds the chart week, the chart date, and a map from player id to value.
- [ ] `T{n}.{pid}.value` reads "{name}'s trade value was {v} before the trade." with one recorded number.
- [ ] `T{n}.{rid}.value` reads "{team} gave {x} and got {y} in trade value." The sums cover listed players only.
- [ ] A traded player with no value gets no player value fact, and the side fact adds ", with {name} unlisted" for each such player.
- [ ] A trade with draft picks adds "; the pick is not valued" or "; the picks are not valued" to the side fact.
- [ ] The side fact exists only when at least one player in the trade has a value.
- [ ] Both facts carry the team and player names like the v2 trade facts, and every number in the text is in the fact's numbers.
- [ ] The vocabulary gains the term **trade value**: the half-PPR redraft trade value from the chart for the week of the trade. It shapes the grade and never appears on the page.
- [ ] A fixture JSON of parsed chart values for week 6 holds every traded player and a few more. Tests build the week 6 trade bundle with it and assert each clause above, including the no-match case.
- [ ] `uv run pytest -q` passes.
