# 25: A starter on IR is out now in weak spots and in trade ideas

Spec: `.scratch/front-door/PRD.md`. Source: H12 of `.scratch/front-door/HANDS-ON.md`.

**App:** API

**What to build:** Bo Girds has Lamar Jackson on IR as its only QB. Live Sleeper gives his status as IR, and the live snapshot reads it. Two causes hid it.

1. The weak spots Topic reads the starters of the roster grade (`managers.grade.roster_starters`). The grade reads only the projections ahead, so Lamar filled the QB slot at QB18, inside the line, and no hole showed. Weak spots now marks each starter who cannot play now as a hole, with `can_play_now` in the slice. The slice also holds `weak_starting_slots`, the list that `/find` reads. An empty slot now is the weakest spot of the block.
2. `/find` served an empty list from the result cache of the API. That list was stored before ticket 13, and ticket 13 did not bump `DOCUMENT_VERSION`. `DOCUMENT_VERSION` is now 22, so no list stored under the old fill serves.

**Blocked by:** 13

**Status:** in-review

- [x] Weak spots for Bo Girds names QB as the weakest spot, "QB empty now", with a hole at QB.
- [x] The weak spots slice holds `weak_starting_slots` with "QB: empty", as `/find` reads it.
- [x] `DOCUMENT_VERSION` is 22, so a finder list stored before ticket 13 never serves.
- [x] Live on port 8102: trade ideas for Bo Girds runs the partner filter and builds 95 offers.

Follow-ups, not in this ticket:

- A live snapshot on the Tuesday after the cutoff saves Sleeper week 9 into `clients/cpc/data/2026/history/week-09/`. That overwrites the hand-patched scores of rosters 5 and 10 (111.46 and 92.71 go back to 76.5 and 64.71).
- The depth word of the slot ranks still comes from the grade, so a QB row can read "fine · hole: Lamar Jackson".
