# 02: Schedules, depth charts, and points allowed per position

**What to build:** The snapshot gains the three slow sources the later adjusters read: the NFL schedules for byes and the week 15 to 17 opponents, the depth charts for the handcuff test, and points allowed per position per defense. The schedules and the depth charts are new nflverse downloads in the same shape as the injuries download, each with a cache and a callable fetch seam. Points allowed is computed from the weekly stats already on disk. A fetch command fills the cache, and the analyze command's as-of line names the three sources.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] A schedules download caches the season's games and reads, per NFL team, the bye week and the opponents for weeks 15 to 17.
- [x] A depth charts download caches the latest depth chart and reads, per NFL team and position, the ordered player list for the week.
- [x] Points allowed per position per defense is computed from the weekly player stats through a given week, and each defense gets a rank per position.
- [x] Each download takes a fetch callable, so tests run with no network. The cache has the same age rule as the injuries cache.
- [x] When a download fails, the reader returns none and the snapshot records the source as missing. Nothing raises.
- [x] The snapshot builder from ticket 01 loads the three sources from the cache when present, and leaves them empty with a missing note when not. If ticket 01 is not merged yet, build the readers and the fixtures alone and leave the snapshot wiring to the merge. Left for the merge: `load_slow_sources` in `slow_sources.py` is the loader to wire into the snapshot builder.
- [x] Small fixtures under the test fixtures directory cover each source for the week 6 teams.
- [x] Tests on the fixtures: the bye week and the three late opponents for one team, the depth chart order for one backfield, the points allowed rank for one defense at one position, and the missing-source path for each.
- [x] `uv run pytest -q` passes with no failed test.
