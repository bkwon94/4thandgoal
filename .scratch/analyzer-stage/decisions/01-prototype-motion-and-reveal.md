# 01: Which motion carries idle, wait, and reveal

Map: `.scratch/analyzer-stage/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** open

## Question

The hero of the analyzer page has three states: idle, wait, and reveal. One motion must carry all three. Brian must see it before he chooses, because "flashy" is a call made by eye.

The prototype shows three options side by side, each in all three states:

1. The extended hero scene of `packages/design/site/parts/` (ADR 0027). Idle is a calm drift, with one light or chip for each added player. Wait is a swarm around the trade chips. Reveal settles the lights into the Lean scale. This is the favorite, because it matches the rest of the site.
2. A scrolltide option, such as a shader or a WebGL field. Search scrolltide first. Fetch a prompt only for an option that goes into the prototype.
3. A second scrolltide option of a different kind.

Each option shows the trade on stage and the stage lines of decision 02 as stub text. Each option shows the staged reveal of about 1 second: the motion settles, the Lean word lands, the scale fills, then the Case and the side tabs rise in. Each option needs a check with motion off and a check on a phone.

The design bar applies: transitions-dev, scrolltide, apple-design, animate, critique, and polish. A scrolltide option that wins needs an ADR beside ADR 0027.

## Decision

None yet.
