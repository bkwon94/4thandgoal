# 08: Can Brian still block a merge with his own word

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** grill

**Blocked by:** 06

**Status:** done

## Question

With the Judge in place, Brian needs a cheap way to stop a merge when his own dev server check finds a problem.

## Decision

Brian decided on 2026-11-06, in a grill.

Yes. A FAIL from Brian for a test, in a PR comment, overrides the Judge and turns the check `verdict` red. Brian never needs to post PASS. `cpc:review` treats his FAIL as a finding.
