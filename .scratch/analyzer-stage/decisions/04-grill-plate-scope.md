# 04: Does the hero text with no plate box go to every hero

Map: `.scratch/analyzer-stage/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

Every hero of the site sets its text on a `plate`, the utility at `apps/site/src/app/globals.css:478`. The plate paints a box of the band color with a soft shadow that spreads 8 px. It keeps the grid and the glow off the letters, so the text contrast passes axe. Brian finds the box ugly where it sits on the corner glow.

Decision 01 removes the plate from the analyzer hero. A soft, light hole in the canvas under each text takes its place. The spec must know if this method stays on the analyzer hero only, or if the spec changes every hero.

The options:

1. The analyzer hero only. A later quick run brings the method to the other heroes. This is the recommendation, because each hero has its own art, so each one needs its own contrast check.
2. Every hero, in this spec. A hero with a static grid and a CSS glow has no canvas to cut a hole, so it needs another method.

## Decision

Every hero, in this spec. Brian chose option 2 on 2026-11-16, against the recommendation of option 1.

- The spec removes the plate box from the text of every hero, not only the analyzer hero.
- The `plate` has 50 uses in 19 files: the heroes of the week, the managers, the midseason report, the sim replay, the egg hunt, the front door, and the 404 page. The spec grows about twice as big.
- Most of those heroes have the static grid and a CSS glow, with no canvas. The method of decision 01, a light hole in a canvas, does not work there. Decision 05 picks the method for them.
- Some plate uses are on a dark surface that is not a hero, such as `bullet-rows.tsx`, `side-tabs.tsx`, `grade-popover.tsx`, and `egg-board.tsx`. Decision 05 also decides if those change.
- Each changed hero needs an acceptance test that its text reaches 4.5:1.
