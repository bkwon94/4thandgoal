# 03: How do we find the Paths, and what do they cost on Fly?

Map: `.scratch/playoff-paths/MAP.md`.

**Kind:** research

**Blocked by:** 02

**Status:** done

## Question

A Path is a set of results of other teams that, with a Finish, reaches the Goal. The code must find the top Paths of each Finish from the 10,000 runs, and the Clinch lines of each team for the League board. Find a method that gives a short, readable Path of up to 3 teams, with its odds. Measure the cost per What-if call on Fly at `shared-cpu-1x`, and the size that `sim.json` adds for all 12 teams and all Goals. Brian wants no extra cost. Name the fallback if the cost is too high.

## Decision

The code finds Paths by a greedy cover: it adds the condition on another team that moves the odds most, such as "X wins at most 1 of 3", and stops at 90% or at 3 teams. A Path needs 400 runs or more, because at 100 runs its odds move up to 19 points between seeds. The odds of a Path are counts of runs, so they are exact up to sample noise. Only 11% to 34% of the open Finishes reach 90% with 3 teams. A Finish under about 50% shows its best Path below 90%, and decision 06 sets that copy.

The Clinch lines come from an exact count of every result of this week, in the weekly build only: 1.3 s for cpc, 0.01 s for NorCal. The API keeps the Paths after a What-if on `shared-cpu-1x`, at no extra cost. The sim loop writes the results of each run as it goes, so a cpc What-if stays near 2.0 to 2.1 s on Fly against the 2.5 s bar of AT-22 of `season-sim`. The spec times it on Fly. `sim.json` takes the small shape: a Week plan for each Finish only, and full Paths only for the spot and bye Goals, about 44 KB gzip at cpc week 10.

If the time on Fly passes 2.5 s, the fallbacks are, in order: Paths only for the Goal on screen, then no Paths after a What-if. The research agent decided this from throwaway scripts on cpc weeks 6, 10, and 11 and NorCal week 10, 2026-11-24. Notes: `decisions/03-research-path-search-cost.notes.md`.
