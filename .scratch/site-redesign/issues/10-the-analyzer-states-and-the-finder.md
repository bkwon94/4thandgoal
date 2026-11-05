# 10: The analyzer states and the finder

Spec: `.scratch/site-redesign/PRD.md`. Acceptance tests AT-24, AT-25, AT-26, AT-27, and AT-40.

**App:** site

**What to build:** The analyzer shows its states in the look. Loading folds the form and shows "Grading the Trade" in the hero. The verdict fills the hero, with the fairness block under it. A trade of 3 teams or more shows one row for each team with TO and FROM tags. An error unlocks the form and shows "Try Again". A client with `finder = true` shows the "Find a Trade" card under the form.

**Blocked by:** 09

**Status:** ready-for-agent

- [ ] Each state shows against the live API, in both themes, at 375, 768, and 1280 px.
- [x] The result text, the error lines, and "Suggested Counters · No counters yet." match `main` for the same trade.
- [x] Only NorCal shows the finder card.
- [ ] The local dev server runs for Brian after the build.
- [ ] The evidence of AT-24, AT-25, AT-26, AT-27, and AT-40 is recorded in `EVIDENCE.md`.
