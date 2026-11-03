# 03: The league-sized numbers move into the config

**What to build:** The numbers that would change with a different league leave the tunables and join the config: the playoff spots, the bye count, the last regular and season weeks, the return-by week, the star and line ranks, the strength rank, and the seller gap. The tunables keep the algorithm settings: the trade bands, the simulation runs, the weights, the waiver sizes, and the API limits.

**Blocked by:** 02, 05, 08

**Status:** done

- [ ] Each moved number has one definition, in the config, with its comment carried over.
- [ ] Every reader of a moved number takes it from the config parameter.
- [x] The tunables module has none of the ten named numbers. Three grade ranks that name twelve teams stay for ticket 18, with the other team-count literals the review found.
- [ ] The four golden tests pass with no golden change.

## Comments

- 2026-10-31: the first build attempt stopped. The ten numbers have readers in twelve modules with no config in reach: adjusters, ranks, trade_facts, manager_grade, facts_league, odds, sheet, the three waiver modules, sleeper, and the API cache. Most read through the snapshot in about forty call sites. Decision: this ticket runs after 05 and 08 merge, so no file is edited in two places at once. Design: `Snapshot` carries the `LeagueConfig` it was built from, set in `week_snapshot` and the live snapshot, so the snapshot readers take the numbers from `snapshot.config`. The odds and the standings take `config` as a parameter. A test that builds a `Snapshot` passes `cornerstone_config()`. The ticket may touch more than twelve files; it is one logical change.

- 2026-11-01: merged into `modular` from branch `modular-03-league-numbers`, six commits 2dd73ab to 558be47, the merge 41a2dd2, and the fix 33afaee. 1,509 tests collected. 57 files. `Snapshot.config` is required; the standings, the odds, the sheet, and the waiver board take `config`; the Sleeper provider takes the two week numbers as plain parameters. `config.lines` replaces `ranks.LINES`. `rubric.md` names the lower-case fields. Two reviewers passed it after one fix pass.
