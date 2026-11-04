# cornerstone.sheet

## Knows

- The wire code of the week build: `build_bundle` passes the chapter source of each package that the client takes.
- `CHAPTER_SOURCES` maps a package name to its source. Today it holds the rankings chapter only.
- `sheet/rankings.py` holds the rankings chapter, the odds facts, the power facts, and the odds call of each build.

## Ports

- `RANKINGS` in `sheet/rankings.py` implements `ChapterSource` of `week/sheet/port.py`, the chapter port of the week.

## Does not do

- It builds no chapter of the week. The week package `week.sheet` builds each one.
- It holds no odds engine. `cornerstone/odds.py` holds it, and the rankings chapter calls it once per build.
- It writes no page. `week/page.py` writes `page.json`.
