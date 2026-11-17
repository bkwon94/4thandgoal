# 05: How hero text with no plate stays readable on a hero with no canvas

Map: `.scratch/analyzer-stage/MAP.md`.

**Kind:** prototype

**Blocked by:** 04

**Status:** open

## Question

Decision 04 removes the plate box from every hero. The `plate` utility at `apps/site/src/app/globals.css:478` paints a box of the band color with a soft shadow, so the grid and the corner glow stay off the letters and the text contrast passes. Brian finds the box ugly.

The analyzer hero cuts light holes in its canvas (decision 01). Most other heroes have the static 24 px grid and a CSS glow, with no canvas. The spec needs a method for them. Brian must see it, because the box was a call made by eye.

Options for the prototype, each on a real hero with the glow under text, such as the manager hero and the week hero:

1. A CSS mask on the grid and the glow layer, shaped to the text blocks, as decision 01 does on the canvas.
2. Move and size the glow so that it never sits under text, and keep the grid faint enough to pass with no plate.
3. A very light plate: no spread, a small blur, and a fill that fades at its edges, so no box shows.

The prototype also answers a second question: do the plate uses on a dark surface that is not a hero change too? Examples are `packages/analyzer/site/form/bullet-rows.tsx`, `side-tabs.tsx`, `packages/managers/site/page/grade-popover.tsx`, and `packages/eggs/site/board/egg-board.tsx`.

Each option needs a contrast check of 4.5:1 by pixel samples, because axe cannot read the art layer. If the method removes the `plate` utility from the site, the spec needs an ADR, because a future reader will ask why the text has no plate.

## Decision

None yet.
