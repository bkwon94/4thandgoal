# 04: The analyzer and 404 heroes move to the slots

Spec: `.scratch/hero-slots/PRD.md`. Acceptance tests AT-9 and AT-12.

**App:** site

**What to build:** A manager opens `/analyze/`, grades a trade, or hits a page that does not exist, and each hero uses the six slots. The analyzer result ends at the fairness block with no empty gap. The 404 title reads "Page not found", and the big "404" shows as art in `feature`. If the easter-eggs PR #19 merged first, its egg on the 404 still works.

**Blocked by:** 01

**Status:** in-review

- [x] The analyzer form and the analyzer result use the slots, as the table of the spec maps them.
- [ ] The analyzer result of grade-clarity trade A shows no empty area for stats or an action, from a run on the real API (AT-9).
- [x] The 404 `h1` reads "Page not found", and a large "404" shows in the hero (AT-12).
- [ ] The easter egg of the 404 still works, if it is on the Spec branch.
- [x] The tests of the analyzer and 404 heroes pass with the new slots.
