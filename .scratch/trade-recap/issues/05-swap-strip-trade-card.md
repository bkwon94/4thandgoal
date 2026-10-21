# 05: The swap strip trade card

**What to build:** The trade card shows the sides as columns across the card. Each column has the team avatar and name, a GETS label, and one chip per player: the headshot on top, a red rule, the name, and this week's points or "0 · bench". A two-side trade has a red FOR tag on a thin divider between the columns. A trade of three or four sides wraps the columns two per row with no FOR tag. The recap stays under the body. Picks render as a plain row in the column. Prototype B in the scratchpad `proto-trade-rows` is the design; Brian picked it and asked for chips a touch smaller.

**Blocked by:** 04 (rebuild week 6 and republish)

**Status:** ready-for-agent

- [ ] The card body is a grid of side columns. Two sides sit side by side with a FOR tag on the divider. Three or four sides wrap two per row with no FOR tag. One side per row never happens.
- [ ] Each column is headed by the team avatar and name, then a GETS label. A long team name wraps and the columns' chip rows still align.
- [ ] Each chip shows the player's headshot cutout on a white band, a red rule, the name, and one line under it: "{points} pts" when he started, "{points} · bench" when he did not, from this week's lines. A player not on either roster's lines this week shows no points line.
- [ ] Chips are a touch smaller than the prototype: about 10 percent less height on the headshot band and the name one step down the type scale. Keep the names readable at 390.
- [ ] Picks render as a plain text row at the bottom of the column.
- [ ] The headshot fetch at build includes every traded player, with the default silhouette on a failed fetch, through the same hook the awards and leaders use.
- [ ] The render context gives each side's players a name, the headshot path, the points, and whether he started; the template reads only the context.
- [ ] Render tests: a two-side card has two columns and one FOR tag; a three-side card has three columns and no FOR tag; a chip shows the bench line for a bench player and the points line for a starter; a pick row renders.
- [ ] The week 6 page renders from the saved data with no writer call. Screenshots at 390 of trade 1 and trade 4, read by a person, no horizontal scroll. Compare against the prototype screenshots.
- [ ] `uv run pytest -q` passes.
