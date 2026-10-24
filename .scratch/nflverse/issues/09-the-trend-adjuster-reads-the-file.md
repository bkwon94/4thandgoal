# 09 — The trend adjuster reads the file

Spec: `.scratch/nflverse/PRD.md`.

**What to build:** The trend adjuster's target share direction reads the nflverse weekly player file through
the usage week, so the analyzer and nflverse agree on a player's targets. When the snap and target shares of
every traded player are flat, the WOPR direction decides for a WR or TE before red zone touches. The
snapshot the API refreshes carries WOPR per player as it carries the shares.

**Blocked by:** 02 The nflverse weekly player file.

**Status:** ready-for-agent

- [ ] With the file present, the target share direction comes from the file's shares. With it missing, from our count, as today.
- [ ] A flat trade where the players a side gets have WOPR up steps up, with a reason that says so, before red zone touches are read.
- [ ] A flat trade with WOPR flat falls through to red zone touches as today.
- [ ] An RB's WOPR never decides, since his touches are carries.
- [ ] The existing rubric tests pass unchanged.
