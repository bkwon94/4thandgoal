# 02: Where does each week's sim file live, and how do the rankings odds switch to the sim?

Map: `.scratch/season-sim/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The weekly build runs the sim and publishes `sim.json`. The spec needs these choices:

1. One season file that each week replaces, or one file in each week folder, which also keeps the history of the odds.
2. How the playoff odds of the rankings page come from the sim in place of `rankings/odds.py`, and what happens to the parity test.
3. How the midseason `sim.json` of week 8 stays as it is, so the midseason report does not change.

## Decision

Brian decided on 2026-11-18, in a grill.

1. **One sim file in each week folder.** The weekly build writes `week-NN/sim.json`, and the sim page reads the latest week. The season file `2026/sim.json` stays as the frozen week 8 file of the midseason report.
2. **The sim replaces the weekly odds engine in full.** The sim also gives the swing of each game next week, by a split of its runs on the winner of each game, as `rankings/odds.py` does now. Then `odds.py` and the parity test go away. ADR 0037 records it.
3. **The past odds stay.** The odds of weeks 1 to 10 in `rankings.json` came from the old engine. They stay as they are, with no rebuild, because the two engines use one model.
4. **10,000 runs each week**, in place of the 5,000 of the old engine. The build pays about 1 s more, and the swings have less noise.

**Why a file when the What-if is live:** Brian asked this. The text of the build quotes the odds: the recaps that Claude writes, the rankings page, and the facts. The file pins one number for the week, so the page and its text agree. The file also lets the page show the odds, Your team, the 3 games, and the replay at once, with no call, and it still works when the API is down. With no picks, the page shows the file and makes no call. The API runs only a What-if with at least one pick.
