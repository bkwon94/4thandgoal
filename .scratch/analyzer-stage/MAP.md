# Analyzer stage: map

App: site.
Spec branch: `analyzer-stage`.

## DESTINATION

One spec for the hero of the analyzer page. The hero lives in three states, idle, wait, and reveal, with one motion story. The trade sits on stage, and stage lines cycle during the wait, so the reader is not bored while the grade runs. The same spec removes the plate box from the text of every hero of the site.

## DECISIONS SO FAR

- The spec covers the analyzer page only: `TitleHero`, `GradingHero`, and the move from `GradingHero` to `ReadHero`. Brian, 2026-11-16 Stage 1 grill.
- The wait mixes three parts: the trade on stage, vague stage lines that cycle and never say "done", and abstract motion. Brian, 2026-11-16 Stage 1 grill.
- The result arrives in a staged reveal of about 1 second: the motion settles, the Lean word lands, the scale fills, then the Case and the side tabs rise in. Brian, 2026-11-16 Stage 1 grill.
- The wait has no minimum time, because a fake delay costs the reader real time. Brian, 2026-11-16 Stage 1 grill.
- The idle hero gets the calm mode of the motion, and each added player shows on the stage. Brian, 2026-11-16 Stage 1 grill.
- The change needs no API change. The analyze call stays one `POST` with no stream. Brian, 2026-11-16 Stage 1 grill.
- The motion is D, "Mesh + light": the hero grid as a live Canvas 2D mesh that weighs the sides, with sparse light pulses, and a flash and a dip toward the favored side at the reveal. The hero text has no plate box. The grade button wraps the ui-sdk `Button`, and its pending state starts the wait. `decisions/01-prototype-motion-and-reveal.md`.
- Every hero of the site drops the plate box from its text, in this spec, with a contrast test of 4.5:1 on each changed hero. Brian, against the recommendation to keep it to the analyzer. `decisions/04-grill-plate-scope.md`.
- The `plate` utility leaves the site. The glow of the static hero art shrinks to `ellipse 38% 46% at 100% 112%`, so it never reaches text. Each plate use off a hero goes too. ADR 0036. `decisions/05-prototype-text-without-plate.md`.
- The stage lines: 12 lines, 2.5 s each, general lines from the measures mixed with lines that name the trade, never "done". `decisions/02-spec-stage-lines.md`.
- The Finder wait keeps `Sweep`. `decisions/03-spec-finder-sweep.md`.

## NOT YET SPECIFIED


## OUT OF SCOPE

- The wait of the front door chat. It is a chat surface with its own motion. A quick run can bring the new loader there later.
- Real progress from an API stream. It moves a seam in both apps and makes the spec about twice as big.
