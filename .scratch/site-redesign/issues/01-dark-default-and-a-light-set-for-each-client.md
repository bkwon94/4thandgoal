# 01: Dark default and a light set for each client

Spec: `.scratch/site-redesign/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, AT-4, AT-37, and AT-39.

**App:** site

**What to build:** Each client opens in dark, and each client has a light option with the theme button. A reader with no stored choice, or with scripts off, gets dark at the first paint. A stored light choice opens in light with no dark flash. NorCal gets a light set for the first time, and CPC gets the light set of decision 09.

**Blocked by:** none

**Status:** in-review

- [x] The brand schema keeps only the `light` and the `dark` sets, both required. A `[fonts]` key, a radius key, or a missing set fails the build and names the key or the set.
- [x] `brand.toml` of CPC and of NorCal hold the light set of the spec table, with the new roles `raised` and `grid` in both sets.
- [x] The token contrast test holds every text pair of each set at 4.5 to 1, the hero pairs among them.
- [x] The static export of each client has `class="dark"` on `<html>`. The boot script removes it only for a stored `"light"`. The test runs the shipped boot script string.
- [x] The fonts and the radii of the look sit in the global CSS, and `rounded-card`, `rounded-sm`, and `font-heading` keep their names.
- [x] Each check of the 19 checks in `decisions/01-research-brand-schema-drops-fonts.notes.md` is changed or replaced.
- [x] ADR 0022 no longer puts the fonts in `brand.toml`.
- [ ] The evidence of AT-1, AT-2, AT-3, AT-4, AT-37, and AT-39 is recorded in `EVIDENCE.md`.
