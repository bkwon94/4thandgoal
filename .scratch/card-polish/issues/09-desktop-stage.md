# 09: Desktop stage

Spec: `.scratch/card-polish/PRD.md`. Acceptance tests AT-25.

**App:** site

**What to build:** From the desktop tier, the ledger of the Index list sits beside a sticky stage. The stage is the hero of the Managers index, built from the six slots of the `hero-slots` spec: the race word, the team name, the record and odds, the four arcs, the grade letter, and the manager link. A hover or a keyboard focus on a row swaps the stage with the wipe and zoom of the Team Roster item.

**Blocked by:** 08, and the `hero-slots` spec merged into `main`

**Status:** ready-for-agent

- [ ] At 1280 px, a hover on The Blue Tent and a focus on Lil Fridge each swap the stage.
- [ ] The stage uses the hero slots, not the old hero part.
- [ ] At 390 px and 768 px, the ledger of ticket 08 shows with no stage.
- [ ] `make check-fast` passes.

## Comments

- 2026-11-08, cpc:implement: blocked until the `hero-slots` spec merges into `main`. Brian chose to build ticket 10 now without the stage check; a second start builds 09 and adds the stage to the floor check.
- 2026-11-08, cpc:implement second start: `hero-slots` merged into `main` as #20 (f9304b5e), and `main` is merged into `card-polish`. The ticket builds now.
