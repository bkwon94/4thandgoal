# 12: How does dark become the default?

Map: `.scratch/site-redesign/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

Dark is the default for every client, and light is always an option. The CSS now has light as the base and a `.dark` override (ADR 0007). One way keeps the `.dark` override and puts the class on `<html>` at build time. The other way inverts the blocks to a `.light` override. The spec picks one, with the effect on `BOOT_SCRIPT` and `paintOf`. See `decisions/01-research-brand-schema-drops-fonts.notes.md`.

## Decision

The site keeps the `.dark` override block of ADR 0007. The build puts the `dark` class on `<html>` for every client. `BOOT_SCRIPT` removes the class for a stored `"light"` choice and does nothing else. `paintOf` loses the branches of a one-set brand, so every client gets the root class, the boot script, and the theme button. We chose this over a `.light` override, because the inversion changes every `dark:` variant for no gain to the reader. A reader with scripts off gets dark.

The spec `PRD.md` records it under Implementation Decisions. Brian approved the spec on 2026-11-05. The record is ADR 0024.
