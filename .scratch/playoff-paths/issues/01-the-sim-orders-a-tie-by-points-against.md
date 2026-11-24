# 01: The sim orders a tie by Points Against

Spec: `.scratch/playoff-paths/PRD.md`. Acceptance tests AT-1 and AT-2.

**App:** pipeline

**What to build:** The sim orders the standings by wins with the median game counted, then Points For, then the higher Points Against, then the roster ID, as Sleeper does (decision 02). The records of a team gain Points Against. The new key reaches all three places that sort teams: the seed order of the season draw, the order of the page block, and the order of the standings table.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] NorCal 2026 week 8 puts roster 9 above roster 1, as the Sleeper `bracket.json` of week 8 does.
- [ ] The top 6 of `cpc` weeks 6 to 10 and `norcal` weeks 8 to 10 equal the Sleeper seeds of each week.
- [ ] A sim package test covers a tie on wins and Points For that Points Against breaks.
- [ ] `make check-fast` passes.
