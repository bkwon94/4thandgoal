# Analyzer stage: map

App: site.
Spec branch: `analyzer-stage`.

## DESTINATION

One spec for the hero of the analyzer page. The hero lives in three states, idle, wait, and reveal, with one motion story. The trade sits on stage, and stage lines cycle during the wait, so the reader is not bored while the grade runs.

## DECISIONS SO FAR

- The spec covers the analyzer page only: `TitleHero`, `GradingHero`, and the move from `GradingHero` to `ReadHero`. Brian, 2026-11-16 Stage 1 grill.
- The wait mixes three parts: the trade on stage, vague stage lines that cycle and never say "done", and abstract motion. Brian, 2026-11-16 Stage 1 grill.
- The result arrives in a staged reveal of about 1 second: the motion settles, the Lean word lands, the scale fills, then the Case and the side tabs rise in. Brian, 2026-11-16 Stage 1 grill.
- The wait has no minimum time, because a fake delay costs the reader real time. Brian, 2026-11-16 Stage 1 grill.
- The idle hero gets the calm mode of the motion, and each added player shows on the stage. Brian, 2026-11-16 Stage 1 grill.
- The change needs no API change. The analyze call stays one `POST` with no stream. Brian, 2026-11-16 Stage 1 grill.

## NOT YET SPECIFIED

- Which motion carries idle, wait, and reveal: the extended hero scene, or one of two scrolltide options? `decisions/01-prototype-motion-and-reveal.md`.
- What do the stage lines say, and how fast do they cycle? `decisions/02-spec-stage-lines.md`.
- Does the Finder wait take the new loader, or keep `Sweep`? `decisions/03-spec-finder-sweep.md`.

## OUT OF SCOPE

- The wait of the front door chat. It is a chat surface with its own motion. A quick run can bring the new loader there later.
- Real progress from an API stream. It moves a seam in both apps and makes the spec about twice as big.
