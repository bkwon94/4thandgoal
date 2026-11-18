# 02: Where does each week's sim file live, and how do the rankings odds switch to the sim?

Map: `.scratch/season-sim/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** open

## Question

The weekly build runs the sim and publishes `sim.json`. The spec needs these choices:

1. One season file that each week replaces, or one file in each week folder, which also keeps the history of the odds.
2. How the playoff odds of the rankings page come from the sim in place of `rankings/odds.py`, and what happens to the parity test.
3. How the midseason `sim.json` of week 8 stays as it is, so the midseason report does not change.

## Decision

None yet.
