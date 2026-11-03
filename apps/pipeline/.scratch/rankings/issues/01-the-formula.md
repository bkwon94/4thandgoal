# 01: The formula

**What to build:** A pure function that takes the history and a week and returns twelve rows: the roster, the power rank, the movement, and the four component ranks, as of that week. The four components are standing, form, schedule played, and scoring, each a number from 0 to 1 and a rank from 1 to 12, as the spec defines them. The power score is the weighted mean, with the four weights in one tunable, equal at 0.25. The power rank sorts by score, best first, tie by the standing rank. Movement is last week's rank minus this week's, and week 1 has none. The median game counts in the standing only. No trade value enters. The glossary gets power rank, power score, component, all-play record, quality win, and movement.

Spec: `.scratch/rankings/PRD.md`, sections "The formula" and "Glossary".

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] The function returns twelve rows for every week from 1 to the given week of the fixture history.
- [ ] The power ranks of a week are a permutation of 1 to 12. So is each component rank.
- [ ] Week 1 has no movement. Week 2 movement equals the week 1 rank minus the week 2 rank.
- [ ] A team on 3 head-to-head wins in a row has a better form rank than the same team with 1 win in the last 3, on a fixture built for it.
- [ ] A win against a team in the top 4 lifts the schedule rank against the same record with no such win.
- [ ] A game against no top-4 team gives the quality half a neutral 0.5.
- [ ] A change to one weight changes the result, in a test that sets the weight through the tunable.
- [ ] The function reuses the season records and the streak code and adds no second copy of either.
- [ ] The glossary has the six terms as the spec words them.
- [ ] `make test` passes. Lint count on the branch is no higher than on main.

## Comments

- 2026-10-22: built on `rankings-formula` at `47a53dd`, two Opus reviews, one fix pass. Awaits Brian merge with `--no-ff`.
