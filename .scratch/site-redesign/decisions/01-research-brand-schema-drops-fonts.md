# 01: How does the brand schema drop the fonts and the radii?

Map: `.scratch/site-redesign/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The look now owns the fonts and the radii, so `brand.toml` keeps only the color roles, the logo, and the copy. Find each reader of `fonts`, `radius_card`, and `radius_small` in `packages/design`, `apps/site`, and the tests. Find each check that breaks, such as `apps/site/src/app/brand-tokens.test.ts`. The spec needs the list of changes and the new shape of `BRAND_SCHEMA`.

## Decision

The brand schema keeps only the `light` and the `dark` sets, and both are required. It keeps `additionalProperties: false`, so a stale `[fonts]` key or radius key fails the build. The fonts and the radii of the look go into the `@theme static` block of `apps/site/src/app/globals.css`, beside the spacing and type tokens. That file already holds the look, its values are the same for every client, and `brand-tokens.test.ts` already reads it. The component classes `rounded-card`, `rounded-sm`, and `font-heading` keep their names, so no component changes.

Only the site build and `packages/design` read the three keys. The pipeline, the API, and the Python packages do not read `brand.toml`. The notes list 19 checks that break, each with its change. The record of ticket 03 must also change lines 10 and 13 of ADR 0022, which put the fonts in `brand.toml`.

Notes: `decisions/01-research-brand-schema-drops-fonts.notes.md`. Claude decided from the research, 2026-11-05.
