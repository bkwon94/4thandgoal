# 10: Do we pay the bundle cost of the Drawer on every page?

Map: `.scratch/ui-sdk-sheet/MAP.md`.

**Kind:** grill

**Blocked by:** 07

**Status:** open

## Question

The `Drawer` adds about 43 KB gzip to each page that imports it (decision 07). The menu sheet sits in `TopBand`, so a direct import adds it to every page. The move removes no library to offset it. The spec must choose:

1. A direct import: every page pays about 43 KB gzip, and the sheet opens with no wait.
2. A lazy import on the first tap of the menu button, or on hover and focus: pages pay nothing until a reader opens the menu, but the first open may wait for the chunk.

A later ui-sdk component may share part of the cost. Decision 07 did not measure that share.

## Decision

None yet.
