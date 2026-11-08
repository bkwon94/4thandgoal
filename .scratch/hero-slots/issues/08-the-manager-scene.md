# 08: The manager scene

Spec: `.scratch/hero-slots/PRD.md`. Acceptance tests AT-18 and AT-36.

**App:** site

**What to build:** A manager opens the manager page of roster 7, and the hero draws one light per played week: weeks 3, 4, and 8 bright for a win, the other five dim for a loss, against a dashed median of each week. Week 8 shows its label at rest. A tap on the grade mark still opens the grade popover.

**Blocked by:** 01 and 07

**Status:** in-review

- [x] The scene of AT-18 shows 8 lights with the right tones and the median line, at 375, 768, and 1280 px.
- [x] The label "Week 8 · 118.89 · W" shows at rest.
- [x] A tap on the grade mark opens the grade popover (AT-36).
- [x] `pnpm check:floor` passes for `cpc`.
