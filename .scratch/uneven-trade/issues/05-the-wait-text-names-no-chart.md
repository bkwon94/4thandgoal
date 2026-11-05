# 05: The wait text names no chart

Spec: `.scratch/uneven-trade/PRD.md`. Acceptance tests AT-13 and AT-14.

**App:** site

**What to build:** While the analyzer runs, the trade form reads "This can take up to a minute early in the week." The finder reads "The search tries every small swap. This can take up to a minute early in the week."

**Blocked by:** none

**Status:** ready-for-agent

- [x] The test of the trade form checks the new wait text, test-first.
- [x] A test of the finder checks its new wait text.
- [x] No text a manager reads in the form or the finder names a chart.
- [x] `pnpm check:fast` passes in the site.
