# Rubric

The rubric grades each side of a proposed trade with a letter from A to F. Code sets the start
letter. The numbers live in the tunable table, `src/cornerstone/tunables.py`. This file names them
and never repeats their values, so the table is the one place to change a number.

## Letters

- A: the side gets far more than it gives.
- B: the side gets more than it gives.
- C: the two sides are about even.
- D: the side gives more than it gets.
- F: the side gives far more than it gets.

## Start letter

Each side gets a start letter from the trade value of the players it gets and the players it
gives. Divide the sum it gets by the sum it gives. Find the band of that ratio. Each band includes
its lower bound.

- `BAND_A` and up starts at A.
- `BAND_B` and up starts at B.
- `BAND_C` and up starts at C.
- `BAND_D` and up starts at D.
- Below `BAND_D` starts at F.

When a side gives no trade value and gets some, it starts at A. When both sides are at zero, both
start at C.

## Consolidation

Two good players must not beat one great player on a plain sum. When one side gives exactly one
player and gets two or more, divide the depth side's sum by `CONSOLIDATION_MARGIN`. The depth side
is the side that gives two or more. Both sides use the divided sum in their ratios. A trade of
three for two, or of any two or more for two or more, gets no discount.

## Unlisted

A traded player with no row on the chart week's chart is unlisted. He has no trade value. When any
player in the trade is unlisted, neither side gets a start letter from trade value. Both sides
start at C, and the breakdown names the unlisted player. When the week has no chart at all, both
sides start at C too.

## Adjusters

After the start letter, each adjuster moves a side by one step at most: up, down, or not at all.
The breakdown lists every adjuster in this order, with its step and a one-line reason.

## Roster fit

Find the side's best lineup before the trade and after it. The best lineup fills the league's
roster slots with the players who have the most points per game over the last `LINEUP_WEEKS`
completed weeks. The fixed slots fill first. Then each flex slot takes the player left with the
most points per game who can play there. At equal points, the position order breaks the tie: RB
over WR, WR over TE, TE over QB, QB over K, K over DEF.

- A lineup loss of `FIT_THRESHOLD` or more is one step down.
- A lineup gain of `FIT_THRESHOLD` or more is one step up.
- The side that gets the single highest-value player in the trade, with no lineup loss, gets one
  step up. A lineup change smaller than `FIT_THRESHOLD` is no lineup loss. Trade value picks that
  player. When the week has no chart or a traded player is unlisted, points per game pick him.
- In a trade of one player for two or more, the side that gets two or more gets the step up only
  when every player it gets starts in its best lineup after the trade.

## Standing

A contender holds one of the `PLAYOFF_SPOTS` playoff spots by record. The standings rank by wins,
then by points for. A seller has more than `SELLER_GAP` wins fewer than the team in the last
playoff spot. Every other team is in the middle and gets no step.

- A contender gets one step up when its best lineup gains now. It also gets one step up when it
  gets a player due back by week `RETURN_BY_WEEK`.
- A contender gets one step down when its best lineup loses now and it gets a player who is due
  back after week `RETURN_BY_WEEK` or not at all.
- A seller gets one step up when it gets the highest-value player in the trade.
- A seller gets one step down when it gives that player for a lineup gain now.

A return week comes from the returns file, `data/<season>/returns.json`, which the commissioner
keeps. It holds the week each injured or suspended player returns. A player who is out, on IR, or
suspended, and who has no row in the file, counts as not back by week `RETURN_BY_WEEK`.

## What the breakdown never holds

The breakdown and every text made from it hold no trade value, no sum, no ratio, no chart name,
and no lineup total. They hold the letter, the adjuster steps, and plain reasons only.
