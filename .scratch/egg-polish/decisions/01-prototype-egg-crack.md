# 01: Which crack variant makes the egg opening an event?

Map: `.scratch/egg-polish/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

The find card cracks the egg now: the halves fly apart and the letter tile springs up. Scrolltide has no egg crack. Contour Reveal has a crack that spreads from the tap point, and Particle Text forms a word from dots. The spec needs one variant that Brian saw and chose. The design uses Claude Design.

## Decision

Variant B, with the squash of variant A at the start. Brian chose it on 2026-11-08 after a look at the canvas.

1. The tap squashes the egg for about 0.15 s, so the tap gets an answer at once.
2. The crack starts at the tap point. Six jagged crack lines draw out from it, and the egg shakes harder as they draw.
3. A light grows inside the egg at the tap point, as the cracks draw.
4. At about 0.56 s the shell bursts. The two halves fly apart along a zigzag through the tap point, and shards fly out from it.
5. A flash rings out from the tap point. The letter tile grows from the tap point, out of a blur.
6. The letter and its copy show at about 1.3 s.

Each tap gives a new crack, because the lines start at the tap point. The parts are SVG and CSS only, with no WebGL.
With reduced motion, the tap shows the letter at once, as now. A tap by the keyboard cracks from the middle of the egg.

Variant A was the crack of now with better timing, so it did not read as a change. Variant C formed the letter from dots after the burst.
It added 0.35 s to each find, and an egg holds no dots. The canvas is https://claude.ai/artifact/HaTnYegqcyt1VS9eh1c1wq.
