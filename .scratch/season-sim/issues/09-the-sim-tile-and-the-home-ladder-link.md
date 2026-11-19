# 09: The Sim tile and the home ladder link

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests AT-45 to AT-49. Decision 06.

**App:** both

**What to build:** Each week page gets the Sim tile right after Standings and before Next week. The tile reads the page of Your team from `sim.json` in the browser, and shows its odds and the line of more wins, with a link to the sim page. With no team set, it shows the league fact of the build. In a playoff week, it shows the title odds of a team still in, or the favorite fact for a team that is out. The week 17 tile names the champion. The Playoff race ladder of the home page links to the sim page.

**Blocked by:** 08.

**Status:** done

- [x] The `cpc` week 10 page with Bo Girds shows the Sim tile between Standings and Next week, with the numbers of the file and a link to `/sim/2026/` (AT-45).
- [x] With no team set, the tile shows the league fact of the file (AT-46).
- [x] In the playoff fixture, the tile shows the title odds of the top seed, and the favorite fact for the 12th team (AT-47).
- [x] The week 17 tile of the season-end fixture names the champion (AT-48).
- [x] The link of the Playoff race ladder opens `/sim/2026/` (AT-49).
- [x] The site evidence set passes the overlap check at the four sizes.
- [x] `make check-fast` passes.

## Comments

Closes with the squash merge of the spec PR: `season-sim-09` (`a2b21f82`) merged into `season-sim` as `4caa9be4`; fix `d78d6e74` set the text floor of the Sim tile label on 2026-11-18.
AT-45 to AT-49 have PASS in `.scratch/season-sim/VERDICTS.md`.
The builder did not count the files it read; the ticket commits changed 16 files, and the main ones are: apps/site/scripts/client-build.mjs, apps/site/src/app/_routes/sim/week-tile.tsx, apps/site/src/app/_routes/sim/your-sim-tile.tsx, apps/site/src/app/_routes/week/page.tsx, apps/site/src/app/front-door/door-page.tsx, apps/site/src/app/front-door/sim-link.tsx, apps/site/src/app/front-door/standings-ladder.tsx, apps/site/src/lib/client-values.ts.
