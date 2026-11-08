# 06: Moves Trend tiles

Spec: `.scratch/card-polish/PRD.md`. Acceptance tests AT-17 and AT-18.

**App:** site

**What to build:** The Adds, Drops, and Trades tiles of Moves on the manager page take a trend from the moves of each week in `managers.json`: bars for Adds and Drops, and dots for Trades.

**Blocked by:** 05

**Status:** ready-for-agent

- [x] The Blue Tent shows Adds bars 5, 1, 2, 4, 1, 1, 6, and 3 for weeks 1 to 8.
- [x] The Trades tile of The Blue Tent shows dots at week 1 and week 4 only.
- [x] Each of the three tiles has a text of its trend.
- [x] `make check-fast` passes.
