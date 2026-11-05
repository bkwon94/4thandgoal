# 05: The gap that shows the Recent rank

Map: `.scratch/grade-clarity/MAP.md`.

**Kind:** spec

**Blocked by:** 01

**Status:** done

## Question

A Recent rank shows beside the Season rank only on a large gap. The size of the gap is a tunable, such as 12 spots at the position. The spec sets the number in `tunables.py` and names it, after ticket 01 sets the measure.

## Decision

The Recent rank shows only when it differs from the Season rank by 12 spots or more. One number holds for every position: `RECENT_RANK_GAP = 12` in `tunables.py` of the analyzer. Brian approved it with the spec on 2026-11-05. See `PRD.md`, "The ranks in the text".
