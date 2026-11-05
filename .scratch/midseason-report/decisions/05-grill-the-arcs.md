# 05: Which arcs exist, and what are their thresholds?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

An Arc is the shape of a team's season, found from the data. Brian's examples: a team that started slow and is on a hot streak, and a team that started hot and now loses. The spec needs a fixed set of arcs, a threshold for each, the most arcs per team, and the order on the page. Candidates: turnaround, collapse, streak, wire to wire, roller coaster, unlucky contender, and points machine with a bad record.

## Decision

Brian decided it in the grill on 2026-11-05.

- The set has eight arcs: Turnaround, Collapse, Wire to wire, Never got going, Roller coaster, Snakebit, Smoke and mirrors, and Heater.
- The start is weeks 1 to 4. Now is the last 4 weeks played. Good is a win rate of 65% or more in a window. Bad is 35% or less.
- Turnaround is bad then good. Collapse is good then bad. Wire to wire is good in both windows. Never got going is bad in both windows.
- These four arcs count the full record, the head-to-head game plus the median game, so an arc agrees with the standings.
- Heater is an active head-to-head win streak of 4 or more. Roller coaster is two head-to-head streaks of 3 or more in opposite directions. A streak never counts the median game, the same rule as Streak on the line.
- Snakebit and Smoke and mirrors read points, with the measure of ticket 06. The arc names the shape, and the luck chapter gives the numbers.
- A team has at most 2 arcs, and a team may have none. The page orders the arcs by the size of the swing.
