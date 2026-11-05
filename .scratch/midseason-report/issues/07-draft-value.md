# 07: Draft value

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests AT-12, AT-13, and AT-14.

**App:** pipeline

**What to build:** The Sleeper provider fetches the draft picks of the season, and its fake gets the same method. `midseason.json` holds the top 5 steals and busts by draft value, with the injury tag and the "the one that got away" line, for an auction and a snake draft.

**Blocked by:** 01 and 02.

**Status:** ready-for-agent

- [ ] A CPC steal is Matthew Golden at $2, and a bust is A.J. Brown at $39 with "just bad".
- [ ] In NorCal, each pick's cost is its pick number.
- [ ] Tyler Allgeier, drafted by Bo Girds for $2 and dropped, carries the "the one that got away" line.
- [ ] A test of the provider passes the fake, with no patch of the port.
