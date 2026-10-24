# 07 — The shootout fact in next week

Spec: `.scratch/nflverse/PRD.md`.

**What to build:** The next week chapter gets one fact per NFL game of week N+1 where both teams have a
positive pass rate over expected over the last 3 weeks. The fact names the two teams, both rates, and the
league starters in that game by roster. The writer picks the one to mention. No fact for a game where
either team leans run.

**Blocked by:** 04 Team EPA and pass rate over expected.

**Status:** ready-for-agent

- [ ] On the fixture with hand-set rates, a game with both teams positive yields one fact with both rates and the league starters in it.
- [ ] A game with one team at or under zero yields no fact.
- [ ] A team with fewer than 3 weeks of plays uses the weeks it has, and a team with none yields no fact.
- [ ] The next week chapter may cite the facts and no other chapter may.
- [ ] A chapter with the environment missing builds with no shootout fact.
- [ ] Every number in each fact's text is in its numbers.
