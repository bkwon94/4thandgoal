# 03 — Expected points and the expected gap

Spec: `.scratch/nflverse/PRD.md`. Research: `.scratch/nflverse/research.md`, question 1.

**What to build:** The build downloads the ffopportunity weekly file through the existing cache and reads
expected points per player per game, rescaled to the league's half-PPR scoring, and the expected gap,
actual minus expected. The reader checks the file for the Monday night game of week N. When the game is
there, the data reads through week N. When it is not, the data reads through week N-1, and the result says
which week it reads through. The expected window is the last 3 games a player played, and a player with
fewer than 2 games in it has no window gap. A missing file never stops the build.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] The rescale is the file's full-PPR total minus half a point per expected reception plus one point per expected interception, with the reception and interception weights read from the league scoring, not hard-coded.
- [ ] One hand-computed row in the test pins the rescale.
- [ ] With the Monday night game id of week N in the file, the result reads through week N. Without it, through week N-1, and the result carries that week.
- [ ] The window gap is the mean per-game gap over the last 3 games played. One game gives no gap. A bye week is not a game.
- [ ] The build record has a source flag for the file.
- [ ] The nflverse week carries the expected data by Sleeper id, None when the file is missing, as it carries the usage.
- [ ] A small fixture of the file covers the week 6 fixture players, and the reader test runs on it.
