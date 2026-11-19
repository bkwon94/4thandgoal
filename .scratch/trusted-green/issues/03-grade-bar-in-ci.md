# 03: grade-bar in CI

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-29.

**App:** site

**What to build:** The full site check runs the grade-bar project in its norcal pass, so CI runs each check that exists.

**Blocked by:** none

**Status:** in-review

- [x] The full site check runs the grade-bar project while the export holds norcal.
- [ ] The site job of `Check` on the PR shows grade-bar as passed.
- [ ] The site job ends in under 25 min, and the ticket notes its time.
