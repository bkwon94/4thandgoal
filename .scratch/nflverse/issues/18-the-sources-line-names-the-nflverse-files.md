# 18 — The sources line names the nflverse files

Spec: `.scratch/nflverse/PRD.md`, "The trade rubric". Found in the first real grade after the deploy on 2026-10-24.

**What to build:** `_sources_line` in `src/cornerstone/cli.py` prints "Sources: schedules, depth charts, points
allowed." from a fixed string, and names a missing source from `_SOURCE_NAMES`. Tickets 03, 09, and 10 added the
injuries file, the expected points file, and the player weeks file to `REFRESHED_SOURCES` in
`src/cornerstone/live.py`. The line does not name them, present or missing. `_SOURCE_NAMES` gains the three
names, the present line builds from the names not missing, and the snapshot marks each of the three as missing
when its file is absent.

**Why:** The line is the one place the grader shows which data it read. It hid three sources on the first grade.

**Blocked by:** None.

**Status:** open

- [ ] A grade with every file reads "Sources: schedules, depth charts, points allowed, injuries, expected points, player weeks."
- [ ] A grade with no expected points file reads "Sources missing: expected points."
- [ ] Every existing cli test passes unchanged.
