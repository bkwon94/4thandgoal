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

## What the breakdown never holds

The breakdown and every text made from it hold no trade value, no sum, no ratio, and no chart
name. They hold the letter and a plain reason only.
