# 05: Drops

Spec: `.scratch/waiver/PRD.md`.

**What to build:** The file gains the drops bucket: rostered players in this league whose snap share
fell for `DROP_WEEKS` (3) weeks in a row and whose rest of season projection is below the best free
agent at their position. Top 8 by the margin. Each row names the roster that holds him and the pool
player who beats him, so the sheet can say "Lil Fridge holds Ekeler, and Estime projects 2.1 points
a week higher".

**Blocked by:** 02 Usage and environment.

**Status:** ready-for-agent

- [x] A rostered player with three falling weeks and a better pool player at his position lands in drops with his roster named.
- [x] A rostered player with two falling weeks does not land in drops.
- [x] A rostered player with three falling weeks and no better pool player does not land in drops.
- [x] The drops bucket sorts by the projection margin and holds at most 8.
- [x] `DROP_WEEKS` is a tunable.

## Comments

2026-10-23, decisions the ticket left open:
- A drop candidate is a `WaiverPlayer` with a `drop` field, a `DropInfo` with the roster ID, the holder team name, the reason `three_falls`, the pool player who beats him, and the margin. A pool player has `drop` as None, so the site reads `if player.drop`. The JSON has no type tag.
- The three falls need a snap share in each of weeks N-3 to N. A bye or a missed week breaks the run, so such a player is not a drop candidate that week.
- `USAGE_SAVED_WEEKS` is `DROP_WEEKS + 1`, so the saved usage always covers the window.
- The best pool player is the one with the highest rest of season projection at the position. The margin is his projection minus the drop candidate's, over the weeks N+1 to 17, rounded half up to one decimal. The fact writes it in the page form, so a margin of 3.0 reads "3".
- A projection equal to the best pool player's is not below it, so that player stays out.
- The bucket holds the top 8 by the margin, then the player ID, with no cap per position. One roster can hold several drop candidates at one position.
- A drop candidate has only the drop fact. The scores are 0, as the bucket never ranks by board score.
- The pool and the drops bucket share one rest of season sum in `waiver_projection.py`.
- A manager with a team pick sees his own drop candidates first: the site does this, not the engine.
