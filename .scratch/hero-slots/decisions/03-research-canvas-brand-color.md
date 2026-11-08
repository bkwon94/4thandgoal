# 03: How the canvas gets the brand colors

Map: `.scratch/hero-slots/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

A canvas color takes plain numbers, but the brand colors are CSS custom properties, and `--color-accent-glow` is a `color-mix` value. Each client has its own `apps/site/src/generated/brand.css`. How does the canvas get the RGB numbers of the grid color, of `on-dark-muted`, and of the glow center for the client that the build runs?

Compare at least two paths:

1. Read the computed color of a hidden element once in the browser and convert it to numbers. Check what Safari on iOS and Chromium return for a `color-mix` value and for an `oklch` value.
2. Write fixed triplets at build time from `brand.toml` into the generated client values.

The answer must also give the position of the glow center in the hero box, from the `.hero-texture` rule of `apps/site/src/app/globals.css`, so the pull aims at it.

## Decision

None yet.
