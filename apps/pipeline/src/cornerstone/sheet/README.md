# cornerstone.sheet

## Knows

- The wire code of the week build: `build_bundle` passes the chapter source of each package that the client takes.
- `CHAPTER_SOURCES` maps a package name to its source. Today it holds the rankings chapter only.

## Ports

- `RANKINGS` of the rankings package implements `ChapterSource` of `week/sheet/port.py`, the chapter port of the week.

## Does not do

- It builds no chapter. The week package builds each week chapter, and the rankings package builds its own chapter.
- It holds no odds engine. The season sim of the sim package is the one engine (ADR 0037). `SIM_ODDS` of `cornerstone/season_sim.py` runs it once per build.
- It writes no page. `week/page.py` writes `page.json`, and `rankings/published.py` writes `rankings.json`.
