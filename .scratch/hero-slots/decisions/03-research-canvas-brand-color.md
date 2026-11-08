# 03: How the canvas gets the brand colors

Map: `.scratch/hero-slots/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

A canvas color takes plain numbers, but the brand colors are CSS custom properties, and `--color-accent-glow` is a `color-mix` value. Each client has its own `apps/site/src/generated/brand.css`. How does the canvas of the scene get the RGB numbers of the brand red, of `on-dark`, of `on-dark-muted`, and of the grid color, for the client that the build runs?

Compare at least two paths:

1. Read the computed color of a hidden element once in the browser and convert it to numbers. Check what Safari on iOS and Chromium return for a `color-mix` value and for an `oklch` value.
2. Write fixed triplets at build time from `brand.toml` into the generated client values.

The prototype of decision 06 read the computed CSS of the page tokens. The research checks if that holds in Safari on iOS for each client, and for the light theme, where the hero stays dark.

## Decision

None yet.
