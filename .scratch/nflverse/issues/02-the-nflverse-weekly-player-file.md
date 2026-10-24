# 02 — The nflverse weekly player file

Spec: `.scratch/nflverse/PRD.md`. Research: `.scratch/nflverse/research.md`, question 2.

**What to build:** The build downloads the nflverse weekly player file through the existing cache and reads
target share, air yards share, and WOPR per player per game for the QB, RB, WR, and TE positions. The usage
week carries the two new shares. Its targets and target share come from the file when the file is there and
from our count when it is not, and the build record says which. A missing file never stops the build.

**Blocked by:** 01 The target count drops two-point tries.

**Status:** ready-for-agent

- [x] The usage week has `air_yards_share` and `wopr`, in percent as the other shares are, None when the file is missing.
- [x] With the file present, a player's targets and target share equal the file's row. With it missing, they equal our count.
- [x] A player with no gsis id in the id map keeps our count and the two new shares are None.
- [x] The build record has a source flag for the file, true on the fixture and false with the file gone.
- [x] The file reads through the cache with the same max age as the other nflverse files, so a rebuild makes no network call.
- [x] A small fixture of the file covers the week 6 fixture players, and the reader test runs on it.
