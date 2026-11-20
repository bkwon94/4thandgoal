# 07: What the CI target is, and which jobs it covers

Map: `.scratch/design-checks-speed/MAP.md`.

**Kind:** grill

**Blocked by:** 02

**Status:** open

## Question

The map set the CI `check` job to drop from about 540 s to 360 s or less. Ticket 02 found that the whole run takes 754 s, and the longest job sets that time. The notes are `02-research-baseline-times.notes.md`.

| Job | Median time |
| --- | --- |
| site-browser | 746 s, of which the Playwright test step is 666 s |
| pipeline | 375 s |
| api | 233 s |
| site-unit | 201 s |

The Bun swap speeds up only site-unit. The `node_modules` cache saves at most 3 s, because the install takes 1 to 3 s.

Decide:

1. Does the target change, or does the spec add work for site-browser and pipeline, such as Playwright shards?
2. Does the `node_modules` cache stay in the speed list, given a gain of 3 s at most?

## Decision

None yet.
