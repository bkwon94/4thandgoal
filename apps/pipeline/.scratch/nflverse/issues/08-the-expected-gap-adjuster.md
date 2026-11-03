# 08 — The expected gap adjuster

Spec: `.scratch/nflverse/PRD.md`.

**What to build:** The trade rubric gains a seventh adjuster, expected gap, last in the order. A side steps up
one when its gets run under expected by the gap tunable or more over the expected window, or its gives run
over by the same. A side steps down one when its gets run over by the gap, or its gives run under. An up
case and a down case together give no step. The reason names the players
and their gaps. Handcuffs and players due back do not count, by the same rule the trend adjuster uses, and
that rule lives in one place. The adjuster sits behind a tunable that starts off, so no live breakdown
shows it until a real trade checks out. The snapshot the API refreshes carries the window gap per player.

The expected data gives expected points per game only. The window gap takes the player's games and his
weekly points from the snapshot's Sleeper stats, the same points the trend adjuster reads.

**Blocked by:** 03 Expected points and the expected gap.

**Status:** done 2026-10-24

- [x] With the tunable on, a side that gets a player 4 under expected steps up, and the reason names him and the gap.
- [x] A side that gives a player 4 over expected steps up.
- [x] A side that gets a player 4 over expected steps down, and a side that gives a player 4 under steps down.
- [x] A side that gets one 4 under and gets another 4 over, or gets under and gives under, takes no step.
- [x] A handcuff's gap and a due-back player's gap do not count, and the reason says so as the trend adjuster does.
- [x] A player with fewer than 2 games in the window has no gap and does not count.
- [x] With the tunable off, no breakdown holds the adjuster and every existing rubric test passes unchanged.
- [x] The gap tunable starts at 3 points per game, and both tunables carry a reason comment.
- [x] The glossary's adjuster entry lists expected gap. It does already; keep it so.
