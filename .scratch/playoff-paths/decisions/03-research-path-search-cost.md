# 03: How do we find the Paths, and what do they cost on Fly?

Map: `.scratch/playoff-paths/MAP.md`.

**Kind:** research

**Blocked by:** 02

**Status:** open

## Question

A Path is a set of results of other teams that, with a Finish, reaches the Goal. The code must find the top Paths of each Finish from the 10,000 runs, and the Clinch lines of each team for the League board. Find a method that gives a short, readable Path of up to 3 teams, with its odds. Measure the cost per What-if call on Fly at `shared-cpu-1x`, and the size that `sim.json` adds for all 12 teams and all Goals. Brian wants no extra cost. Name the fallback if the cost is too high.

## Decision

None yet.
