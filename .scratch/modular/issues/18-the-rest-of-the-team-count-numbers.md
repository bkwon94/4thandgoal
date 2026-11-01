# 18: The rest of the team-count numbers

**What to build:** Ticket 03 moved ten league-sized numbers into the config. The review found more that depend on the team count: `GRADE_SPARE_RANK`, `GRADE_STRONG_RANK`, and `GRADE_SOFT_RANK` in the tunables, whose comments name twelve teams; `TEAM_COUNT` in `facts_league`; `SHOOTOUT_TOP`, which names "of the 12"; the `n(12)` facts in the leaders and trades chapters; and the `(12, 36)` rankings range in the sheet base. Each one moves into the config or reads the team count from it. The team count itself comes from the league file at parse time, so the config may hold it as a field set from the provider, or the readers may take `len(teams)`.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] `grep -rn "12" src/cornerstone/tunables.py src/cornerstone/facts_league.py src/cornerstone/sheet/` finds no team-count literal.
- [ ] A test with a config for a ten-team league changes the grade spare rank and the rankings range.
- [ ] The four golden tests pass with no golden change.
- [ ] `make typecheck` passes.
