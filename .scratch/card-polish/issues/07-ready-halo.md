# 07: Ready halo

Spec: `.scratch/card-polish/PRD.md`. Acceptance tests AT-19, AT-20, and AT-21.

**App:** site

**What to build:** The Grade button of the Stack wears a halo, after the Send Halo item, that glows brighter as the trade fills. The level is the count of passed checks over three times the count of sides, where each side checks a team, a get, and a give. The halo reaches full only when the ready rule passes. It uses the accent role of the brand, reads in both themes, and drops any pulse under reduced motion.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] A unit test proves the level for zero, two, and six passed checks of a two-side trade, and full only when the ready rule passes.
- [ ] On `/analyze/`, two teams and no player give the level of 2 of 6, below full.
- [ ] The removal of a player from a full trade dims the halo.
- [ ] The halo reads in the light theme, and reduced motion shows no pulse.
- [ ] `make check-fast` passes.
