# 01: Byes on the next-week games and in the page JSON

Spec: `.scratch/next-week-byes/PRD.md`, "Key starters and byes, in the pipeline", "The page JSON", "Thin data".
Glossary: **Key starter**, **Bye line**. ADR 0006.

**What to build:** The weekly build knows, for each team in each next-week game, every rostered player on
bye next week, key starters first. The page JSON carries that list on each side of each game, so the
site can draw the bye line. A build with a thin schedule or a thin history writes empty lists and logs
one line.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [x] The past week model keeps each roster's starters for that week, read from the saved matchups. The empty slot "0" is not a starter.
- [x] A pure function gives a roster's key starters from its starters per completed week: 3 of the last 4, then 2 of 3, then 2 of 2, none under 2 weeks. QB, RB, WR, TE only. FLEX counts. The counts are tunables.
- [x] A player's bye is his NFL team's bye from the nflverse schedule. Next week is the page week plus one.
- [x] Each side of a next-week game carries `byes`: `{ player_id, name, position, key }`, key starters first, then by position rank, then by name. Position rank may wait for ticket 02; until then the rest sort by name.
- [x] The renderer writes `byes` on each side in the page JSON. An empty list for a team with nobody on bye. The schema version does not change.
- [x] No schedule, no history, or fewer than 2 completed weeks: empty lists, one log line that names the missing source, no raise.
- [x] Tests on the week 6 fixture bundle read the lists. Unit tests cover the key starter rule with 4, 3, 2, and 1 weeks, a FLEX start, a new add, a K and a DEF. The thin data case has a test.
- [x] `uv run pytest -q` and `uv run ruff check src tests` pass.
