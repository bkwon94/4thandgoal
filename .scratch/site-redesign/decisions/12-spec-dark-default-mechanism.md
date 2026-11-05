# 12: How does dark become the default?

Map: `.scratch/site-redesign/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** open

## Question

Dark is the default for every client, and light is always an option. The CSS now has light as the base and a `.dark` override (ADR 0007). One way keeps the `.dark` override and puts the class on `<html>` at build time. The other way inverts the blocks to a `.light` override. The spec picks one, with the effect on `BOOT_SCRIPT` and `paintOf`. See `decisions/01-research-brand-schema-drops-fonts.notes.md`.

## Decision

None yet.
