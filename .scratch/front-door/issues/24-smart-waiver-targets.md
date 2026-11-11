# 24: The Waiver targets Answer reads each free agent with Jev

Spec: `.scratch/front-door/PRD.md`. Source: row H5 of `.scratch/front-door/HANDS-ON.md`.

**App:** api

**What to build:** The waiver list of ticket 15 still read the published `waiver.json`, so it held weak players such as Drew Sample. The Topic now builds live in the API. Code takes the free agents by hard rules only: on no roster now, at QB, RB, WR, or TE, with a week or a rest of season projection above 0, inside a cost cap of 48. Each candidate gets his facts: the projections, the last 3 weeks, the Sleeper adds, and the depth chart with each player above him who is out. The team need comes from `weak_starting_slots`, the starters with their week projections, and the byes ahead. One Jev request per candidate asks an add Noul and a stash Noul. Claude writes the Answer from the kept players only, and quotes no bid.

**Blocked by:** 15

**Status:** in-review

- [x] The candidates follow the hard rules and the cost cap only: no rostered player, a trade position, a projection above 0, and at most 48.
- [x] The facts of each candidate say why he trends: the Sleeper adds, the depth chart place, each player above him out now, and the last 3 weeks.
- [x] The team need names an empty QB slot when the only healthy QB leaves and the other QB is on IR.
- [x] One Jev request per candidate, in waves. A player above 0.7 on the add or the stash Noul stays, best first.
- [x] Claude reads the kept players only. With none, the Answer says that no free agent beats the starters.
- [x] The block lists the kept players in the same shape, so the site needs no new type.
- [x] The key covers the candidate facts, so a roster change or a new injury gives a fresh Answer. A kept Answer keeps its block.
- [x] The trending list stays 30 minutes per client.
- [ ] Brian reads the live Answer for Bo Girds and one other team.
