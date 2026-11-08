# 02: The tune of the bent grid on a phone

Map: `.scratch/hero-slots/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** wontfix

## Question

What values make the bend look right on a real phone, and does the canvas grid line up with the CSS grid?

Build one hero with the canvas on a throwaway route. Brian opens it on his phone. The prototype answers four things:

1. The values of `reach`, `depth`, and the peak alpha for the pull on entry and for the tap pulse. The start values are reach 140, depth 0.6 for the entry and 0.5 for a tap, and a peak alpha of about 0.5.
2. Does the canvas grid line up with the CSS grid of 24px from the corner at 0,0, or does a double grid show? The other path is a canvas that is clear at rest and fades in for the bend only.
3. Does the bend show in the gaps between the text plates, with the pull aimed at the center of the brand glow?
4. Does the scroll still start on the hero, and does a tap on a link or on the grade popover still work?

The check of the readability floor must still pass with the canvas on the page. Text sits on a plate, so the contrast of the text does not change.

## Decision

Replaced on 2026-11-07. Decision 06 made the art of the hero a scene of the week's data, so the bend of Mesh Flow does not ship and needs no tune. Brian decided this in the prototype of decision 06.
