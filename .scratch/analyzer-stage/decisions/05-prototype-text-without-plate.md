# 05: How hero text with no plate stays readable on a hero with no canvas

Map: `.scratch/analyzer-stage/MAP.md`.

**Kind:** prototype

**Blocked by:** 04

**Status:** done

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

Brian chose option 2, variant B "Glow moved", on 2026-11-16, from a prototype of five variants on desktop and on his iPhone.

### What B is

- No hero text has a plate. The `plate` utility leaves the site.
- The glow of `.hero-texture` is smaller and lower: `radial-gradient(ellipse 38% 46% at 100% 112%, var(--color-accent-glow), transparent 70%)`. The old glow was `ellipse 70% 90% at 100% 100%`. The grid does not change.
- The bright part of the glow never reaches text. The glow is about half its old size, so the hero is less warm.

### Contrast

A pixel-sample check measured 6 pages for client cpc at 390 px and 1280 px. It hid each text, sampled the brightest pixel under its box, and compared it with the text color.

- With B, every text passes. The worst is the losing score `106.71` of the week hero, `#999999`, at 5.50:1.
- With no plate and no art change, that score measured 4.35:1 to 4.43:1. Every other text passed.
- The check did not reach the egg banner, because eggs are off in cpc, or the norcal client. The spec must hold the check for each changed hero in both clients.

### The plate uses off a hero

- `grade-popover.tsx`, `grade-dial.tsx`, the 404 page, and the midseason opener sit inside a hero. The same glow covers them.
- The egg banner (`egg-banner.tsx`) has its own `.hero-texture`, so the same glow covers it too.
- The egg board already hides its texture behind text. `bullet-rows.tsx` and `side-tabs.tsx` have no plate.
- So the answer to the second question is yes: every plate use goes.

### What was rejected

- `A` "Mask", a soft hole in the art under each text block: a dark patch still showed behind the scores, and it needs a script to measure each block.
- `C` "Soft plate", a fill with faded edges: a faint dark blob still sat on the glow.
- `D` "None": the control. It fails 4.5:1 on one score.

### Notes for the build

- The `plate` utility also adds padding and a negative inline margin. The spec decides if a text keeps that space when the plate goes.
- The analyzer hero keeps the canvas holes of decision 01.
- ADR 0036 records the decision.
- The prototype code is deleted from the repo. A copy for reference, with the contrast script and the screenshots, is in `~/plans/analyzer-stage-prototype/plate-05/`. Rewrite it properly. Do not copy it into the product as is.
