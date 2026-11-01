# 03: The league-sized numbers move into the config

**What to build:** The numbers that would change with a different league leave the tunables and join the config: the playoff spots, the bye count, the last regular and season weeks, the return-by week, the star and line ranks, the strength rank, and the seller gap. The tunables keep the algorithm settings: the trade bands, the simulation runs, the weights, the waiver sizes, and the API limits.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] Each moved number has one definition, in the config, with its comment carried over.
- [ ] Every reader of a moved number takes it from the config parameter.
- [ ] The tunables module has no number that names the team count or the league calendar.
- [ ] The four golden tests pass with no golden change.
