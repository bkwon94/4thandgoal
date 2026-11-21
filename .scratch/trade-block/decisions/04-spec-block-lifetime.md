# 04: How long the Trade block lives

Map: `.scratch/trade-block/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

The lean is that the block lives in page state only, and a change of Your team clears it. The spec records this, and what happens to the block on a mode switch to Grade and back.

## Decision

The block lives in the page state of Find mode only. A change of "Your team" clears it. A change of the partner or the chip keeps it. A switch to Grade and back keeps it exactly when it keeps the partner and the chip. Recorded in `PRD.md`, which Brian approved on 2026-11-21.
