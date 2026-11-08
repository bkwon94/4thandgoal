# 03: How the canvas gets the brand colors

Map: `.scratch/hero-slots/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

A canvas color takes plain numbers, but the brand colors are CSS custom properties, and `--color-accent-glow` is a `color-mix` value. Each client has its own `apps/site/src/generated/brand.css`. How does the canvas of the scene get the RGB numbers of the brand red, of `on-dark`, of `on-dark-muted`, and of the grid color, for the client that the build runs?

Compare at least two paths:

1. Read the computed color of a hidden element once in the browser and convert it to numbers. Check what Safari on iOS and Chromium return for a `color-mix` value and for an `oklch` value.
2. Write fixed triplets at build time from `brand.toml` into the generated client values.

The prototype of decision 06 read the computed CSS of the page tokens. The research checks if that holds in Safari on iOS for each client, and for the light theme, where the hero stays dark.

## Decision

Decided on 2026-11-07 from the research in `03-research-canvas-brand-color.notes.md`. The repo facts cite file and line, and the browser facts cite the W3C, WHATWG, and WebKit sources.

1. **The canvas draws three colors only:** `accent`, `on-dark`, and `on-dark-muted`. Each is a plain hex in both clients and in both themes. The schema allows only a hex for a base role (`brand.ts:220`).
2. **The grid and the glow stay in the CSS layer `.hero-texture`.** Two grid roles differ by theme, for example the NorCal `grid` and the CPC `rule-dark`. A color read once at mount goes stale after a switch of the theme. CSS follows the switch for free.
3. **At mount, the scene reads each color from a hidden probe element** with `getComputedStyle(probe).color`, and passes the `rgb()` string to `fillStyle` as it is. A dim light uses `globalAlpha`. The scene never passes a raw `var()` to `fillStyle`, because `fillStyle` drops it with no error.
4. **A brand test holds the three roles equal in the light set and the dark set** of each client, so a read at mount stays correct after a switch of the theme.
5. **Fallback:** if the scene must read nothing from the DOM, the build writes the three triplets from `colorsOf(brand, "dark")` into the client values, and the page passes them down as a prop.

No client uses `oklch` or `color-mix` for these three roles, so the path does not depend on how Safari on iOS reads those strings in `fillStyle`. No primary source confirms that, and the research did not test a real iPhone.

The color of the flare on NorCal is open for Brian: `accent` there is `#c2410c`, an orange, and `accent_text` is a gold.
