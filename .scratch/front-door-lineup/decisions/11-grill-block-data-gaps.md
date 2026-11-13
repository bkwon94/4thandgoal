# 11: Where do the missing fields of the blocks come from?

Map: `.scratch/front-door-lineup/MAP.md`.

**Kind:** grill

**Blocked by:** 04

**Status:** done

## Question

The prototype of decision 04 found four fields with no source in the files:

1. The win odds of one game, for the matchup card. Keep the estimate from the gap of the projected totals and the league `spread` in `sim.json`, or use the odds of the sim?
2. The trade grade, for the trade card. Call the analyzer on the API for a letter grade, or keep the edge in projected points?
3. A FLEX and a DEF rank, for the slot rank bars. Add them to the roster grade, or show only QB, RB, WR, and TE?
4. The league median of norcal, for the recap card. Hide the tick, or compute a median for every league?

## Decision

Brian decided each item on 2026-11-12.

1. The win odds of one game come from the gap of the two projected totals of the week, with the league `spread` of `sim.json` as the noise. The API computes them live with the matchup card of decision 05. They match the two projected scores on the card, and they see a bye, an OUT player, or a Swap. The levels of the season sim see none of these.
2. The trade card closes with the Lean of the Advisor: Send it, Lean yes, Gut call, Lean no, or Pass. The trade card shows only in Trade ideas and Trade check, and both run on the API, where the analyzer runs. The bars of projected points for the rest of the season stay as the mark. The case and the top bullets open in place. The edge line of the prototype goes, so the card has one verdict.
3. The slot rank bars show QB, RB, WR, and TE, the `SLOT_POSITIONS` of the roster grade. A FLEX slot takes an RB, a WR, or a TE, so a FLEX rank counts the same players twice. A DEF rank changes the roster grade of the manager pages, and that change is out of scope.
4. The recap card shows the median tick only in a league that plays the median. cpc plays it, and a cpc record after 9 weeks has 18 games. norcal does not, and `median` is null in its `page.json`. A tick in norcal would look like a game that does not exist.
