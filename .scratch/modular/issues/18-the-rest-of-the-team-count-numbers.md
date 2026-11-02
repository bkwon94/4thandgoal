# 18: The rest of the team-count numbers

**What to build:** Ticket 03 moved ten league-sized numbers into the config. The review found more that depend on the team count: `GRADE_SPARE_RANK`, `GRADE_STRONG_RANK`, and `GRADE_SOFT_RANK` in the tunables, whose comments name twelve teams; `TEAM_COUNT` in `facts_league`; `SHOOTOUT_TOP`, which names "of the 12"; the `n(12)` facts in the leaders and trades chapters; and the `(12, 36)` rankings range in the sheet base. Each one moves into the config or reads the team count from it. The team count itself comes from the league file at parse time, so the config may hold it as a field set from the provider, or the readers may take `len(teams)`.

**Blocked by:** 03

**Status:** done

- [ ] `grep -rn "12" src/cornerstone/tunables.py src/cornerstone/facts_league.py src/cornerstone/sheet/` finds no team-count literal.
- [ ] A test with a config for a ten-team league changes the grade spare rank and the rankings range.
- [ ] The four golden tests pass with no golden change.
- [ ] `make typecheck` passes.

## Comments

- 2026-11-01: merged into `modular` from branch `modular-18-team-count`, commits c86fa8d, 8689707, and 30c1ffe. 1,514 tests collected. `team_count` is a config field, and the weekly and live parses raise if the league file holds another count. `grade_spare_rank`, `grade_strong_rank`, and `grade_soft_rank` are properties of the team count; the quarter rounds down. `shootout_top` stays a plain field set to 4, because its old comment names no formula. The median reads the middle ranks from the list length, since a past week holds no config. Two reviewers passed it after one fix pass.
