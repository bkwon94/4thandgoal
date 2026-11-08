# 03: How does the Grade dial look?

Map: `.scratch/card-polish/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

The Grade dial shows the Roster grade: the letter in the middle and four segments, one for each part (projection, production, trade value, depth). `managers.json` gives each part a rank from 1 to 12. The first try sizes each segment by its weight (45/30/10/15) and fills it by its rank. Brian must see it at the size of a manager card and of Season So Far, with text that axe can read, before the spec fixes it.

## Decision

Brian chose variant B on his phone, on 2026-11-07, after a prototype on the live Managers index and a manager page at 390px. All three variants used the dial method of the Scrolltide Health Tracker item: pill blades on a 210 degree arc, a staggered fill on entry, and instant under reduced motion.

1. The Grade dial is four equal arcs, one for each part of the Roster grade. Each arc has 12 blades, one per team. The lit count is 13 minus the rank, so rank 1 lights all 12. The rank sits in the center of the arc as text, for example "4th". The part name and its weight sit under the arc as text.
2. On a Managers index card, the grade box with the letter stays. The four small arcs sit in one row under the grade read.
3. In Season So Far on the manager page, the letter and the grade read sit on top, and the four arcs sit in a 2x2 grid, each with "of 12" and "N% of the grade".
4. One Grade dial part serves both sizes.

Why not A: A sized four groups on one arc by weight and lit each by rank. The groups had no labels on the arc, so a reader could not tell the parts apart. The lit total is not the grade score, so a C team and an A team looked almost the same. Why not C: one arc filled by a weighted sum of ranks, which is not the grade score either, so it could mislead.

The weights are 45, 30, 10, and 15, from `GRADE_WEIGHTS` in `packages/managers/python/src/managers/tunables.py`. `managers.json` does not carry them. Ticket 09 decides where the site gets them.

The glossary entry for Grade dial changes from "four segments" to "four arcs, one for each part, each lit by its rank". The spec writes it.

The prototype code is deleted. It was never committed.
