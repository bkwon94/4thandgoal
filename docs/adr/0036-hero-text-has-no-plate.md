# Hero text has no plate

Each hero text sat on a plate: a box of the band color with a soft shadow, so the grid and the corner glow never sat under a letter. Brian found the dark box ugly where it sat on the glow. We decided that hero text has no plate. The glow of the static hero art is small and low in the corner instead, so its bright part never reaches text. Brian chose it on 2026-11-16, from a prototype of five methods (spec `analyzer-stage`, decision 05).

## Considered Options

- A mask on the art, with a soft hole under each text block. It passed contrast, but a dark patch still showed behind the scores, and it needs a script to measure each text block.
- A light plate with no spread and a fill that fades at its edges. No edge showed, but a faint dark blob still sat on the glow.
- No plate and no change to the art. The muted score of the week hero measured 4.35:1 on the glow, below 4.5:1.
- A smaller, lower glow. It is the only method with no dark shape behind the text, and it needs no script. The cost is a glow about half its old size.

## Consequences

- The glow of `.hero-texture` is `ellipse 38% 46% at 100% 112%`, not `ellipse 70% 90% at 100% 100%`. A larger glow must pass the contrast test of each hero text again.
- Axe cannot read the contrast of text over a background image, so each hero text needs a pixel-sample check of 4.5:1. The check hides the text, samples the brightest pixel under its box, and compares it with the text color.
- The analyzer hero draws its own art on a canvas, so it cuts a soft hole in the canvas under each text block instead (decision 01).
- A plate use off a hero sits inside a hero, or on the egg banner, which has its own `.hero-texture`. The same glow covers each one.
