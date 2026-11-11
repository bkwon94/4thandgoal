# 48: Under reduced motion, the ask box fades in place

Spec: `.scratch/front-door/PRD.md`. Source: AT-46 in the evidence round of 2026-11-11.

**App:** site

**What to build:** With `prefers-reduced-motion: reduce`, the first question makes the ask box fade, with no glide, no blur, and no spring. Today the ask box vanishes for about 2 frames, then shows at the bottom with no fade.

**Blocked by:** none

**Status:** done

- [x] Red first: a test under reduced motion that samples the opacity of the ask box each frame after the first send. The opacity never jumps from 1 to 0 in one frame.
- [x] The ask box and the Answer fade by opacity only.

## Comments
- Closes with the squash merge of the spec PR.
