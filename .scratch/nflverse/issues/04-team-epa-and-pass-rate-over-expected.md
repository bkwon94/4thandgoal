# 04 — Team EPA and pass rate over expected

Spec: `.scratch/nflverse/PRD.md`. Research: `.scratch/nflverse/research.md`, question 3.

**What to build:** The team week carries EPA per play and pass rate over expected per game, from the play by
play we already hold. Both sums read pass and run plays only, with two-point tries left out, where both
columns are always present. No new download.

**Blocked by:** 01 The target count drops two-point tries.

**Status:** ready-for-agent

- [ ] The team week has the EPA sum and the pass rate over expected sum, and the environment reader gives EPA per play and pass rate over expected per team per week.
- [ ] A two-point try, a kneel, a spike, and a special teams play add nothing to either sum.
- [ ] A test on the play by play fixture pins one team week by hand.
- [ ] The existing environment tests pass unchanged.
