# 03: The sim engine and sim.json

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests AT-3, AT-37, AT-38, and AT-51.

**App:** pipeline

**What to build:** The build runs the sim of the rest of the season through the playoff bracket and publishes `sim.json`: the odds of 10,000 runs per team, the seed odds, the final-win odds, the parameters, and 200 sim runs. The bracket reseeds after round 1 when the league's settings say so. The report gets the sim result through a port of `midseason`, wired by the app.

**Blocked by:** 01 and 02.

**Status:** done

- [x] Two builds of CPC week 8 give the same `sim.json`, byte for byte.
- [x] `sim.json` holds 200 sim runs and the odds of 10,000 runs, and its gzip size is 50 KB or less.
- [x] In a CPC sim run, seed 1 meets the lowest seed left in the semifinal.
- [x] The parity test passes: the playoff odds of the sim are within 2 points of the published week 8 odds of CPC and NorCal.
- [x] `clients/cpc/published/2026/rankings.json` does not change.

## Comments
- Closed by the merge of PR #13.
