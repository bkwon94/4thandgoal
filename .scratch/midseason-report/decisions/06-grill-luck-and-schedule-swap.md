# 06: How does the report measure luck, an overachiever, and the schedule swap?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The luck chapter names the luckiest teams and the overachievers. The schedule swap gives each team's record under every other team's schedule. The spec needs the measures. Choices: the all-play record, the expected wins from points, the points against, the median game of each client, and close-game luck. The glossary has Season numbers and Season pace, so the new terms must not conflict with them.

## Decision

Brian decided it in the grill on 2026-11-05.

- **All-play wins** is the sum of a team's weekly all-play win rates. A team that beats 9 of 11 teams in a week gets 0.82 for that week.
- **Schedule luck** is head-to-head wins minus All-play wins. The median game stays out, because its result depends only on the team's own score.
- Schedule luck is the one measure. One table ranks every team by it. "Overachiever" is a word in the prose, not a measure.
- A team at +1.5 or more gets the Smoke and mirrors arc. A team at -1.5 or less gets the Snakebit arc. This sets the measure that ticket 05 left open.
- The **Schedule swap** is a 12 by 12 grid. A row is a team, a column is a schedule, and the diagonal is the real record.
- In a swap, team A plays B's opponent each week with A's own score. In the week that B played A, A plays B.
- CPC cells add the team's own median results, so the diagonal matches the standings. NorCal has no median game, so its cells are head to head only.
- The chapter calls out the best schedule that each team missed, and the team with the most records better than its own.
- Two context lines show per team: points against with its rank, and the close-game record. A close game is a head-to-head margin under 5 points. Neither line feeds a measure, an arc, or a rank. The writer may cite both.
- A tie counts half a win in the head-to-head record, the all-play rate, and the swap grid.
- The span is weeks 1 to the report week. A week with no score for a team does not count.
- Each page that shows the All-play record explains it in one plain sentence. The power rankings note already does.
- The "luck" chapter is the Schedule luck chapter. The "injury luck" chapter is the Injury toll chapter, because it measures starter games lost, not chance. Its content does not change.
