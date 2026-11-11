# 29: One step pattern for every wait

Spec: `.scratch/front-door/PRD.md`. Source: H16 of `.scratch/front-door/HANDS-ON.md`.

**App:** site

**What to build:** each Answer kind waits in its own form. Every kind now uses one `Steps` component: small mono step lines inside the Answer card, a `braille` spinner from `unicode-animations` on the live step, ✔ on a done step, a static dot under reduced motion. One first line for every kind. Steps stay above the Answer. The gaps fill: a "Writing…" step in the personal Topic, quiet placeholder chips in the dock, a pending state on Send. One `Shimmer` copy at most.

**Blocked by:** 26

**Status:** in-review

## Done

- [x] One `Steps` component in `apps/site/src/app/front-door/steps.tsx`, used by free, trade check, trade ideas, sell high, personal, waiver, and the routing wait.
- [x] The live step shows the `braille` spinner of `unicode-animations` 1.0.3 at 80 ms. A done step shows ✔. Reduced motion shows a static dot and runs no frame timer.
- [x] One first line for every kind: "Reading the league…". `Steps` adds the one "…" of a live line.
- [x] Trade steps stay above the Answer, each one done, and no longer fade out.
- [x] A "Writing…" step sits under the personal data block until the check comes.
- [x] Quiet placeholder chips hold the dock until the browser reads the day.
- [x] Send holds busy with the spinner while a question routes.
- [x] One `Shimmer` remains, for the fixing line of a free answer.
- [x] The trade stream sends no check, so trade kinds show no "Checking" mark.
