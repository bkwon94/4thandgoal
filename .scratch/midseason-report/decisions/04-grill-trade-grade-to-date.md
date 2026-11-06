# 04: What is the rubric of a trade's grade to date?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

Each trade gets a grade on what happened after it: the points of the players since the trade, the team results since the trade, and injuries right after the trade. The analyzer already grades a proposed trade, and the glossary reserves Verdict and Trade value. The spec needs: the inputs of the grade to date, its scale, its name in the glossary, and how it differs from the analyzer's grade, so the two do not conflict.

## Decision

Brian decided it in the grill on 2026-11-05.

- The look back is a **Trade result**, not a Grade. Grade stays the analyzer's letter for a proposed trade.
- The measure is the net Points over the line of each side since the trade: what it got and started, minus what it gave away as the other team started those players.
- The labels are Robbery, Clear win, Slight edge, Push, and Too soon. Too soon means fewer than 2 weeks since the trade. The spec sets the gap lines from the real spread, so CPC shows about 3 or 4 Robberies and Clear wins.
- The record of the team since the trade shows on the card as context, such as "4-1 since". It does not count in the result.
- "Hurt on arrival" tags a player who was out in the first week after the trade.
- "Since" starts at the first week whose games come after the trade, per the Trade window. A flipped player counts only during his stint.
- In a 3-team trade, each side gets its net, and the label comes from the gap between the best side and the worst side.
- The page shows every trade: the top 3 as full cards, then the rest as a compact list.
