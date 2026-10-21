# 05: The swap strip trade card

**What to build:** The trade card shows the sides as columns across the card. Each column has the team avatar and name, a GETS label, and one chip per player: the headshot on top, a red rule, and the name. A two-side trade has a red FOR tag on a thin divider between the columns. A trade of three or four sides wraps the columns two per row with no FOR tag. The card has no recap under it. The trade chapter and its writer call leave the weekly build, with its facts, rules, and vocabulary. The page footer goes. Picks render as a plain row in the column. Prototype B in the scratchpad `proto-trade-rows` is the design; Brian picked it and asked for chips a touch smaller.

**Blocked by:** 04 (rebuild week 6 and republish)

**Status:** done

- [x] The card body is a grid of side columns. Two sides sit side by side with a FOR tag on the divider. Three or four sides wrap two per row with no FOR tag. One side per row never happens.
- [x] Each column is headed by the team avatar and name, then a GETS label. A long team name wraps and the columns' chip rows still align.
- [x] Each chip shows the player's headshot cutout on a white band, a red rule, and the name. The chip has no points line.
- [x] Chips are a touch smaller than the prototype: the headshot band is 64px high and the name is one step down the type scale. The names stay readable at 390.
- [x] Picks render as a plain text row at the bottom of the column.
- [x] The headshot fetch at build includes every traded player, with the default silhouette on a failed fetch, through the same hook the awards and leaders use.
- [x] The render context gives each side's players a name and the headshot path. The template reads only the context.
- [x] No recap renders under the card. The trade chapter and its writer call leave the weekly build, with its facts, rules, and vocabulary.
- [x] The page footer is gone.
- [x] Render tests: a two-side card has two columns and one FOR tag. A three-side card has three columns and no FOR tag. A pick row renders. A traded DEF gets the team logo.
- [x] The week 6 page renders from the saved data with no writer call. Screenshots at 390 of trade 1 and trade 4 show no horizontal scroll.
- [x] `uv run pytest -q` passes.
