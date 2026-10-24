# 10 — The lineup value of a player due back

Spec: `.scratch/nflverse/PRD.md`, "The trade rubric". Brian's case on 2026-10-24: Lamar Jackson.

**What to build:** The roster fit adjuster builds each side's best lineup from points per game over the last
4 completed weeks, so a player with no game in that span counts as 0 and a trade that gets him shows no lineup
gain. A player due back, one the returns file lists with a return week after the last completed week, takes
his lineup value from the Sleeper projection ahead instead: the mean of his weekly projections from his return
week through the last regular week, a bye as no game. Every other player keeps his recent points per game, since
recent points carry form. The fit reason names the due-back player, his return week, and the projection he counts
for. The snapshot carries the projections ahead by player and week from the week's raw file, None when the file
is missing, and then the adjuster grades as today. The live API refresh must have the file fresh on Fly.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] A side that gets a player due back with 0 games in the last 4 weeks and a projection of 18 a game gains the best lineup, and the reason names him, his return week, and the 18.
- [ ] A player not due back keeps his recent points per game, whatever his projection.
- [ ] A player due back with no projection row counts as 0, as today.
- [ ] With the projections file missing, every grade equals today's grade, and the reason says the projections are not available only when a due-back player is in the trade.
- [ ] The projection weeks skip the bye and stop at the last regular week, and a return week after the last regular week gives 0.
- [ ] The finder picks up the change through the grade and needs no edit.
- [ ] Every existing rubric test passes unchanged.
