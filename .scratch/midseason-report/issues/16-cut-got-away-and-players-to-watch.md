# 16: Cut "the one that got away" and Players to watch

Spec: `.scratch/midseason-report/PRD.md`. Acceptance test AT-64. AT-14 and AT-23 are retired.

**App:** both

**What to build:** The report no longer has the "the one that got away" line, in the draft or in the waivers, and no longer has the Players to watch chapter with Due to rise, Due to fall, and Grab him now. The facts, `midseason.json`, the site schema, and the page all drop them.

**Blocked by:** none.

**Status:** ready-for-agent

- [ ] A build of CPC week 8 has no "the one that got away" line and no Players to watch facts in `midseason.json`.
- [ ] The report page has no Players to watch chapter and no Grab him now.
- [ ] The rule tests and the fixtures of the two parts are gone, and no test still expects them.
