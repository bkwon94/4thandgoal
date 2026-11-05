# 03: The superstar check reads the week before

Spec: `.scratch/uneven-trade/PRD.md`. Acceptance test AT-8.

**App:** pipeline

**What to build:** When the snapshot has no chart for the week, the superstar check reads the newest saved chart read of the week before, within the weeks the chart fallback uses. The reason then says "last week". The start letters do not use the earlier read, so both sides still start at C.

**Blocked by:** 02

**Status:** in-review

- [x] A rubric test grades trade W with no week 9 chart and the real saved week 8 read in place, test-first.
- [x] The test shows Teehee's row: "Kenneth Walker III is a superstar, a top 8 player last week." Both sides start at C.
- [x] With no chart this week and no saved read of the weeks before, the row reads "No player it gets is a superstar."
- [x] `make check-fast` passes in the pipeline.
