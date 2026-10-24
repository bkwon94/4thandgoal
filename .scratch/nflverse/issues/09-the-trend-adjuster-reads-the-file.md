# 09 — The WOPR tiebreak in the trend adjuster

Spec: `.scratch/nflverse/PRD.md`.

**What to build:** When the snap and target shares of every traded player are flat, the WOPR direction
decides for a WR or TE before red zone touches. The target share stays the Sleeper share: on real data the
Sleeper weekly target counts equal the nflverse counts every week, so a switch buys nothing, and the saved
extracts never reach the live API on Fly. The WOPR comes from the nflverse weekly player file in the cache,
read by the slow sources through week N-1 as the expected points are, and the file joins the API refresh so
Fly downloads it. The swing is its own tunable, about 8 WOPR points.

**Blocked by:** 02 The nflverse weekly player file.

**Status:** ready-for-agent

- [ ] The target share direction reads the Sleeper share as before; no code path changes it.
- [ ] The snapshot carries WOPR per player per week from the cached file, None when the file is missing, and the API refresh downloads the file.
- [ ] A flat trade where the players a side gets have WOPR up steps up, with a reason that says so, before red zone touches are read.
- [ ] A flat trade with WOPR flat falls through to red zone touches as today.
- [ ] The WOPR direction counts only when all 4 window weeks have a value, and a WOPR that points both ways falls through to red zone touches.
- [ ] The WOPR swing is a tunable with a reason comment.
- [ ] An RB's WOPR never decides, since his touches are carries.
- [ ] The existing rubric tests pass unchanged.
