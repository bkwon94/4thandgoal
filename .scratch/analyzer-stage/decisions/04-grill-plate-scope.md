# 04: Does the hero text with no plate box go to every hero

Map: `.scratch/analyzer-stage/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** open

## Question

Every hero of the site sets its text on a `plate`, the utility at `apps/site/src/app/globals.css:478`. The plate paints a box of the band color with a soft shadow that spreads 8 px. It keeps the grid and the glow off the letters, so the text contrast passes axe. Brian finds the box ugly where it sits on the corner glow.

Decision 01 removes the plate from the analyzer hero. A soft, light hole in the canvas under each text takes its place. The spec must know if this method stays on the analyzer hero only, or if the spec changes every hero.

The options:

1. The analyzer hero only. A later quick run brings the method to the other heroes. This is the recommendation, because each hero has its own art, so each one needs its own contrast check.
2. Every hero, in this spec. A hero with a static grid and a CSS glow has no canvas to cut a hole, so it needs another method.

## Decision

None yet.
