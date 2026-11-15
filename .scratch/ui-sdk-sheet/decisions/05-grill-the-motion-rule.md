# 05: How does a sheet you can drag fit the motion rule of ADR 0024?

Map: `.scratch/ui-sdk-sheet/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

ADR 0024 asks for a strong ease-out and no motion under reduced motion. The ui-sdk `Drawer` settles with a spring and fades under reduced motion.

## Decision

A sheet you can drag follows a spring, and a short fade is allowed under reduced motion. Every other motion keeps the ease-out rule. ADR 0034 records it and amends ADR 0024. Brian decided it in the grill of 2026-11-14.
