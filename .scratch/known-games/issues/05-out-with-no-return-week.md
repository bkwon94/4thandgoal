# 05: Out with no return week

Spec: `.scratch/known-games/PRD.md`, "Out with no return week". Prior art: nflverse ticket 10, the lineup value
of a player due back.

**What to build:** A player whose Sleeper injury status is Out, IR, PUP, Sus, or NA, and who has no week in the
returns file, counts as due back at the return-by week, 14. His lineup value is then his projection ahead from
that week through the last regular week, as for any due-back player. Sleeper projects zero for the weeks he is
out, so his value drops the same day Sleeper tags him. The injury adjuster still docks one step for out with no
near return. The roster fit reason names him, the week he counts as back, and the projection he counts for. A
player with a week in the returns file grades as today. A player with a healthy status grades as today.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] A player tagged Out with no returns entry and 20 points a game over his last 3 games takes his projection ahead from week 14 as lineup value, and the fit reason names him and the 14.
- [ ] The injury adjuster still docks one step for him.
- [ ] A player tagged Out with a returns entry of week 9 takes his projection ahead from week 9, as today.
- [ ] A player tagged Questionable keeps his recent points per game.
- [ ] With no projections file, the Out player keeps his recent points per game and the fit reason says the projections are not available.
- [ ] The cache key changes when a rostered player's status moves into the out set, because the content hash reads the rows the grade now reads.
- [ ] Every existing rubric test passes unchanged.
