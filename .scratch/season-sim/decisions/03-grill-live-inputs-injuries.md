# 03: How live are the inputs of the What-if, and does a season-ending injury lower the level of a team?

Map: `.scratch/season-sim/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** open

## Question

The injuries reach the sim only through the projections. The level of a team comes from its season average, which holds the weeks a now-injured star played. The build reads the injuries once, on Tuesday.

Brian decides:

1. Does the API run the What-if on the Tuesday inputs, or refetch the injuries and the projections from Sleeper when a manager opens the page?
2. Does a season-ending injury of a starter also lower the level of the team, and by how much?

3. Does the API machine move from `shared-cpu-1x` to a size with a full CPU, or does the What-if run fewer runs? At the baseline quota of the shared CPU, one call can take 11 to 15 s.

Ticket 01 found that Sleeper blanks each week of an expected absence, so the projections already see a long injury. The level of the team still holds the weeks the star played.

## Decision

None yet.
