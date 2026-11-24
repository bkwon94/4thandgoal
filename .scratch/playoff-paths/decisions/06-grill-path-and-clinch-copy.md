# 06: What is the copy of a Path, a Week plan, and a Clinch line?

Map: `.scratch/playoff-paths/MAP.md`.

**Kind:** grill

**Blocked by:** 04

**Status:** done

## Question

Each Path, Week plan row, and Clinch line is one plain sentence with its odds. Decide the fixed phrases, such as "Clinches a spot with a win" and "needs team X to lose 2 of 3", the use of "about" for a small sample, and the copy of "Doesn't matter". Say "manager" or "another manager", never "rival". Name no internal part, such as Jev or Finder. Decision 03 found that most Finishes under about 50% have no Path of 3 teams that reaches 90%, so decide the copy of a best Path below 90% too. The copy comes after the layout, because the layout sets the room each line has.

## Decision

Brian approved each line on 2026-11-24, in 5 questions. The examples come from the prototype data of cpc week 11.

**A Path condition** reads as a final record: "Omarion Himpton ends 14-14 or worse." A Finish reads "ends 15-13" too, so the page keeps one form, and the reader does not need to know that the median counts. NorCal reads the same way with no median: "ends 8-6 or worse". A full Path:

> **4-2 · ends 15-13 · 26% likely**
> If Omarion Himpton ends 14-14 or worse, 💿 🐑 ends 16-12 or worse, and Bengals Buddies ends 15-13 or worse.
> Happens 17% · you're in 99%.

**A Finish** takes one of 4 forms:

| Case | Copy |
| --- | --- |
| Odds of 99.5% or more | "You're in whatever the others do." |
| A Path reaches 90% | The Path, then "Happens 17% · you're in 99%." |
| The best Path is below 90% | The header "Best chance", the Path, then "Happens 4% · you're in 62%." |
| Odds under 0.5% | "No way in at this record." No Path shows. |

**A Week plan** has the header "Your plan to 15-13 · you're in 81%", with the "Try it" odds, so the header and the button agree. When the order does not matter, a line reads "Any 4 wins of your 6 work. This is the most common order." Each row:

> **Week 12 · vs Teez Nuts**
> Win and beat the median.
> Score 109 to win, 127 to be sure. Score 108 to beat the median, 114 to be sure.
> Root for: Immaculate Concepcion over Bengals Buddies · Nico Collinsizer over Omarion Himpton

A row with a loss reads "Lose, but beat the median" or "Lose and miss the median", with no Score to beat for the game. "To be sure" means an 80% chance. The week card uses the same words, "to win" and "to be sure", in place of "Coin flip" and "80% sure".

**A Clinch line** names the Goal of the view:

- "Clinches a spot with a win and a median win."
- "Clinches a spot with a win, a median win, and a Teez Nuts loss to Bo Girds."
- "Out with a loss and a median miss." When every loss ends it: "Out with any loss."

A line names at most 2 results beyond the team's own, then "and 1 more result". It shows the most likely way, and the sheet lists every way. No Clinch line shows on a Seed Goal.

**The small words.**

- "about" follows `ABOUT_RUNS = 400` of `packages/sim/python/src/sim/tunables.py`, as in `season-sim`. A Path needs 400 runs, so a Path never shows "about". A Finish row and a root-for number can.
- "Doesn't matter" is a gray tag on a root-for row that moves the odds by less than 1 point. The row stays and names both teams.
- A root-for row: "Immaculate Concepcion beats Bengals Buddies → 55%", with "Bengals Buddies wins → 47%" below in smaller text.
- Median rooting: "Bo Girds misses the median → 58%".
- The copy says "manager" or "another manager", never "rival". It names no internal part, such as Jev or Finder.
