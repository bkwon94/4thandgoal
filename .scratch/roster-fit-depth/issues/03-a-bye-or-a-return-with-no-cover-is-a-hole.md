# 03: A bye or a return with no cover is a hole

Spec: `.scratch/roster-fit-depth/PRD.md`, "The hole kinds", "The line and the bounds". Glossary: "Hole".
Decision record: ADR 0003.

**What to build:** The third hole kind, no cover. A starting slot whose starter has his bye in weeks N to N+2, with
the window as a tunable, is a hole when no bench player at an allowed position above the line is free to cover
him. A starter due back in weeks N+1 to N+2 reads the same way. A starter due back after N+2 is below the line for
this read, whatever his projection ahead ranks. A bench player can cover one slot only. The step rule of ticket 02
applies: a new no-cover hole steps down and blocks the step up. The fit reason names the slot, the player, and
the week of his bye or his return. With no schedule map, no bye hole reads and the reason says the schedules are
not available, as the schedule adjuster does today. The rubric prompt's roster fit section gains the no-cover
kind.

**Blocked by:** 02 (A hole steps the grade).

**Status:** done

- [ ] A starter with his bye in week N+1 and a bench player above the line at his position is no hole.
- [ ] A starter with his bye in week N+1 and no bench cover above the line is a hole, and the reason names the week.
- [ ] A starter with his bye in week N+3 is no hole.
- [ ] Two starters with byes in the window and one bench cover give one hole.
- [ ] A starter due back in week N+2 reads as a bye and needs cover.
- [ ] A starter due back in week N+6 is a hole.
- [ ] A trade that gives away the only bench cover for a bye in the window opens a new hole and steps down.
- [ ] With no schedule map, no bye hole reads and the reason names the missing schedules.
- [ ] The rubric prompt states the no-cover kind, and `ste` passes on the new text.

## Comments

- 2026-11-02: `main` holds the merge 84d9349. Status set to done by the state-file sweep of agent-habits 02.
