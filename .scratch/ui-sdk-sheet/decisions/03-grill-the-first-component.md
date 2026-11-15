# 03: Which component moves first?

Map: `.scratch/ui-sdk-sheet/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Five sheets and some tab and disclosure controls are hand-built. One must go first.

## Decision

`menu-sheet` in `packages/design/site/shell/` moves first. It has the most hand-built drag physics, it shows on the front door, and it sits in `packages/design`, where the rules get set. A desktop never sees it, because the pill bar takes its place. Brian decided it in the grill of 2026-11-14.
