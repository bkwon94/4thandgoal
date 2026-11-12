# 06: The matchup card and the rank mover list from the weekly build

Spec: `.scratch/front-door-lineup/PRD.md`. Acceptance tests AT-24, AT-26, AT-40.

**App:** both

**What to build:** Your last matchup shows the matchup card with the final scores and the two lineups slot by slot, each slot with a bar from the center line for its gap. Your next matchup gets the same card from the weekly build, with projected scores. Power rankings shows the rank mover list: one row per team with the rank, the name, a bar from the center for the move, and an arrow with the number of places.

**Blocked by:** 05

**Status:** ready-for-agent

- [x] The week 9 build of cpc writes a last matchup `block` with 114.07 to 100.63 against Teehee, slot by slot (AT-24).
- [x] The week 9 build writes a `block` for Your next matchup and for Power rankings in both leagues (AT-40).
- [ ] Site screenshots show the matchup card and the rank mover list (AT-24, AT-26).
