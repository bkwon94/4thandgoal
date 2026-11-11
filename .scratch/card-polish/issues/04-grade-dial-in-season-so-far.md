# 04: Grade dial in Season So Far

Spec: `.scratch/card-polish/PRD.md`. Acceptance tests AT-9, AT-11, AT-12, and AT-13.

**App:** site

**What to build:** A Grade dial part in a small and a large size draws four equal arcs, one for each part of the Roster grade, after the Health Tracker dial: 12 pill blades on a 210 degree arc, the lit count the count of teams plus one minus the rank, the rank as text in the arc, and the part name and weight as text under it. Season So Far on the manager page shows the letter, the grade read, and the four arcs in a 2x2 grid. A site constant holds the weights, and a test compares it to `GRADE_WEIGHTS` of the pipeline.

**Blocked by:** none

**Status:** done

- [x] Season So Far of The Blue Tent shows A, the grade read, and arcs 4th, 6th, 7th, and 7th, with 9, 7, 6, and 6 of 12 blades lit.
- [x] Each arc has an accessible name with its part, its rank, and its weight.
- [x] The weights test fails when the site constant differs from `GRADE_WEIGHTS`, and passes when they match.
- [x] The reduced-motion test proves the arcs show lit at once.
- [x] `make check-fast` passes.

## Comments
- Closed by the merge of PR #21.
