# 02: Does the sim break a seed tie the way Sleeper does?

Map: `.scratch/playoff-paths/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

A Finish, a Path, and the tiebreak gap on points are only true if the sim orders tied teams the way Sleeper does. Find the tiebreak rules of Sleeper for `playoff_seed_type` 1 (cpc) and the NorCal setting, from the Sleeper docs or the league data. Compare them with the order in `packages/sim/python/src/sim/season.py`. Record each gap, and say if the median game counts in the record of a tie.

## Decision

Sleeper seeds by the record with the median game counted, then Points For, then the higher Points Against, then a coin flip. `playoff_seed_type` is not a tiebreak: 1 (cpc) reseeds each round, and 0 (NorCal) keeps the bracket fixed. The sim sorts by `(-wins, -points, rid)` at `packages/sim/python/src/sim/season.py:306`, with the same key at `page.py:221` and `standings_table.py:72`. The sim has no Points Against key. NorCal week 8 shows the gap: rosters 1 and 9 tie at 5-3 with equal Points For, and Sleeper seeds roster 9 higher.

The spec adds the higher Points Against as the third key in all three places, and keeps `rid` as a fixed stand-in for the coin flip. NorCal week 8 is the test case. The page assumes no tied games, and the rank of a tied game stays out of this spec. The research agent decided this from Sleeper support docs and the stored brackets, 2026-11-24. Notes: `decisions/02-research-tiebreak-rules.notes.md`.
