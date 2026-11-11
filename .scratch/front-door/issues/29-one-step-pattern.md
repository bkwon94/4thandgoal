# 29: One step pattern for every wait

Spec: `.scratch/front-door/PRD.md`. Source: H16 of `.scratch/front-door/HANDS-ON.md`.

**App:** site

**What to build:** each Answer kind waits in its own form. Every kind now uses one `Steps` component: small mono step lines inside the Answer card, a `braille` spinner from `unicode-animations` on the live step, ✔ on a done step, a static dot under reduced motion. One first line for every kind. Steps stay above the Answer. The gaps fill: a "Writing…" step in the personal Topic, quiet placeholder chips in the dock, a pending state on Send. One `Shimmer` copy at most.

**Blocked by:** 26

**Status:** open
