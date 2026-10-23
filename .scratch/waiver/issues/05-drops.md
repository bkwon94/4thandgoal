# 05: Drops

Spec: `.scratch/waiver/PRD.md`.

**What to build:** The file gains the drops bucket: rostered players in this league whose snap share
fell for `DROP_WEEKS` (3) weeks in a row and whose rest of season projection is below the best free
agent at their position. Top 8 by the gap. Each row names the roster that holds him and the pool
player who beats him, so the sheet can say "Lil Fridge holds Ekeler, and Estime projects 2.1 points
a week higher".

**Blocked by:** 02 Usage and environment.

**Status:** ready-for-agent

- [ ] A rostered player with three falling weeks and a better pool player at his position lands in drops with his roster named.
- [ ] A rostered player with two falling weeks does not land in drops.
- [ ] A rostered player with three falling weeks and no better pool player does not land in drops.
- [ ] The drops bucket sorts by the projection gap and holds at most 8.
- [ ] `DROP_WEEKS` is a tunable.
