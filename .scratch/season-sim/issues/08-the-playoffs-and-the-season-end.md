# 08: The playoffs and the season end

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests AT-42, AT-43, AT-44, AT-66, and AT-69. Decision 06 and the map Q10.

**App:** both

**What to build:** In the playoff weeks, the page block and the page answer for Your team first. A team still in sees its title odds, its game of this round, and two tiles with the odds after a win or a loss. A team that is out sees "Out of the playoffs" and the bracket with the title odds of each team left. Only a bracket game whose two teams are set has tiles. After the final, the page shows the final bracket and the champion, with no result tile and no sim button. The tests use the playoff fixture and the season-end fixture of ACCEPTANCE.md, built from `cpc` 2026 week 10 and stored run 1.

**Blocked by:** 05.

**Status:** ready-for-agent

- [x] The build makes the playoff fixture and the season-end fixture by one command, and the evidence names their seeds and champion.
- [ ] With the top seed as Your team, the Playoffs page shows its title odds, its game, and two tiles (AT-42).
- [x] With the 12th team as Your team, the page says "Out of the playoffs" and shows the bracket with title odds (AT-43).
- [x] The season-end page shows the final bracket and the champion, with no tile and no sim button (AT-44).
- [x] No later round has a tile (AT-66), and the season-end page has no chart of odds by week (AT-69).
- [x] The site evidence set passes the overlap check at the four sizes.
- [x] `make check-fast` passes.
