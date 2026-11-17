# 01: Which motion carries idle, wait, and reveal

Map: `.scratch/analyzer-stage/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

The hero of the analyzer page has three states: idle, wait, and reveal. One motion must carry all three. Brian must see it before he chooses, because "flashy" is a call made by eye.

The prototype shows three options side by side, each in all three states:

1. The extended hero scene of `packages/design/site/parts/` (ADR 0027). Idle is a calm drift, with one light or chip for each added player. Wait is a swarm around the trade chips. Reveal settles the lights into the Lean scale. This is the favorite, because it matches the rest of the site.
2. A scrolltide option, such as a shader or a WebGL field. Search scrolltide first. Fetch a prompt only for an option that goes into the prototype.
3. A second scrolltide option of a different kind.

Each option shows the trade on stage and the stage lines of decision 02 as stub text. Each option shows the staged reveal of about 1 second: the motion settles, the Lean word lands, the scale fills, then the Case and the side tabs rise in. Each option needs a check with motion off and a check on a phone.

The design bar applies: transitions-dev, scrolltide, apple-design, animate, critique, and polish. A scrolltide option that wins needs an ADR beside ADR 0027.

## Decision

Brian chose variant D, "Mesh + light", on 2026-11-16, after five rounds of the prototype on desktop and on his iPhone.

### What D is

- The ground is the grid of the hero itself, as a live mesh on a Canvas 2D. It uses no WebGL. It builds on the scrolltide component `mesh-flow`, with the pulses of the scrolltide `light-cove`.
- Idle: a flat mesh that matches the 24 px grid texture of the hero. It has no pulses.
- Wait: a weight under each side of the trade pulls the mesh down in turn, 1.25 s per side, so the hero reads as "weighing the sides". Sparse accent pulses, with a bright head and a soft tail, run along the mesh lines and bend with the mesh. A pulse runs faster near a weight that pulls.
- Reveal: the lines of the favored side flash once and fade in about 0.6 s. Then the mesh dips toward the favored side and goes flat. The Lean word, the scale, the Case, and the result follow in the staged reveal of about 1 s.
- Motion off: a still, flat mesh. The reveal is a plain fade.

### The text on the hero

- D draws the corner glow on its own canvas, low in the bottom-right corner, away from the labels and the chips.
- No hero text has a plate box. The canvas cuts a soft, light hole in the mesh and the glow under each text block and each chip. The hole dims the art only in part, so it never reads as a dark halo. A small muted label gets a deeper hole, as small as the label.
- Brian rejected the dark plate box and a large dark text shadow as ugly.
- Contrast is not proven yet. Round 5 measured 2.45:1 for the column label of the other side, during the wait, when that weight pulls. A softer weight glow followed and was not measured again. The spec must hold an acceptance test that each hero text reaches 4.5:1 in idle, wait, and reveal.

### The grade button

- The grade button wraps the ui-sdk `Button` in `packages/design/site/ui/`, the one folder that may import `@ui-sdk`.
- Its `onClick` returns a Promise, so the button goes pending. It gets `aria-busy`, `aria-disabled`, and `data-pending`, and it keeps focus through the wait. `pendingAnnouncement` is "Grading the trade". The pending state starts the wait of the hero.
- The label morphs from "Grade the Trade" to "Grading…" with the transitions.dev recipe `33-text-morph`. The ui-sdk docs advise against a change of text while the button is pending. The spec must decide whether to keep the morph.

### The shared motion

- Stage lines: the transitions.dev recipes `28-thinking-states` and `15-shimmer-text`, one line every 2.5 s. Decision 02 sets the text.
- The Case: `18-texts-reveal`. The result cards under the hero: `14-skeleton-reveal`.

### What was rejected

- A, the extended hero scene: the swarm of lights read as messy. A calm version with one arc for each chip was fine, but less strong than B and D.
- The scrolltide shader `magma-flow`: too loud, and heavy on a phone.
- C, `light-cove` alone: high on wow, but it is a new visual language, it needs WebGL, and its pulses tell nothing about the trade.
- B, `mesh-flow` alone: right in meaning, but less wow than D.

### Notes for the build

- The prototype code is deleted from the repo. A copy for reference is in `~/plans/analyzer-stage-prototype/`, outside the repo, with screenshots of D. Rewrite it properly. Do not copy it into the product as is.
- A canvas shadow ignores the pixel-ratio transform, so a mask built with a canvas shadow must scale by the pixel ratio itself.
- `next dev` rewrites `apps/site/next-env.d.ts` and `apps/site/AGENTS.md` when it starts. Check both before each commit.
