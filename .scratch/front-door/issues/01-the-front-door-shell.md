# 01: `/` becomes the front door

Spec: `.scratch/front-door/PRD.md`. Acceptance tests AT-1, AT-2, AT-47, AT-48, AT-49, AT-50.

**App:** site

**What to build:** `/` shows the front door with no hero, no four numbers, no midseason takeover, and no tool tiles. The first visit asks for Your team in a sheet with no skip, and the browser keeps it. An empty Thread shows the ask box at its center. The menu and the dock of both clients keep Home, Week N, Power Rankings, and Managers. Every page stays at its route. The layout sets `viewport-fit=cover`, so the ask box clears the home bar of an iPhone.

**Blocked by:** none. Before this ticket, `cpc:implement` merges `main` into `front-door`, so the branch holds the merge of `manager-brain`.

**Status:** ready-for-agent

- [x] The sheet lists the 12 teams of CPC, with no skip, no close, and no login (AT-1).
- [x] A reload keeps Your team, and no sheet shows (AT-2).
- [x] The menu and the dock of CPC and NorCal show only the 4 links (AT-48). NorCal gets a `[menu]` table.
- [x] The week 8 report, the rankings, the managers, the midseason, and the Trade page render as before (AT-49).
- [ ] The ask box sits fully above the bottom safe area in an iPhone viewport (AT-47).
- [x] Each screen meets the DESIGN BAR of the map, in light and dark.
