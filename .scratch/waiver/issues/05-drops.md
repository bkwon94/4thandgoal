# 05: Drops

Spec: `.scratch/waiver/PRD.md`.

**What to build:** The file gains the drops bucket: rostered players in this league whose snap share
fell for `DROP_WEEKS` (3) weeks in a row and whose rest of season projection is below the best free
agent at their position. Top 8 by the gap. Each row names the roster that holds him and the pool
player who beats him, so the sheet can say "Lil Fridge holds Ekeler, and Estime projects 2.1 points
a week higher".

**Blocked by:** 02 Usage and environment.

**Status:** ready-for-agent

- [x] A rostered player with three falling weeks and a better pool player at his position lands in drops with his roster named.
- [x] A rostered player with two falling weeks does not land in drops.
- [x] A rostered player with three falling weeks and no better pool player does not land in drops.
- [x] The drops bucket sorts by the projection gap and holds at most 8.
- [x] `DROP_WEEKS` is a tunable.

## Comments

2026-10-23, decisions the ticket left open:
- A drop is a `DropPlayer`, a `WaiverPlayer` with the roster ID, the holder team name, the reason `three_falls`, the pool player who beats him, and the gap. The bucket type is a union, so the saved board keeps these fields.
- The three falls need a snap share in each of weeks N-3 to N. A bye or a missed week breaks the run, so such a player is not a drop that week.
- The best pool player is the one with the highest rest of season projection at the position. The gap is his projection minus the drop's, over the weeks N+1 to 17, rounded half up to one decimal. The fact writes it in the page form, so a gap of 3.0 reads "3".
- A projection equal to the best pool player's is not below it, so that player stays out.
- The bucket uses the shared cap: 8 in all, 3 per position. The order is the gap, then the player ID.
- A drop has only the drop fact. The scores are 0, as the drop never ranks by board score.
- A manager with a team pick sees his own drops first: the site does this, not the engine.
