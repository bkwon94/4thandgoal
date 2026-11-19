# 07: The replay on the page

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests AT-38 to AT-41. Decision 04.

**App:** site

**What to build:** "Sim week N" and "Sim the season" open the replay: three screens on one stage that never scrolls, under the site header. The season screen shows the standings in the Race style. The playoff screen plays one round at a time. The champion screen says where Your team finished. "Sim week N" plays "Games", then "Standings". The control bar sits in its own row. The replay picks a stored run with a chance in proportion to its weight, so it follows the set results. Under reduced motion, it uses fades only. The midseason report and its replay do not change.

**Blocked by:** 06.

**Status:** done

- [x] "Sim week 11" plays the games with Bo Girds first and one median line, then the standings in the Race style (AT-38).
- [x] "Sim the season" plays Season, Playoffs, and Champion with no scroll, and the controls stay in their own row (AT-39).
- [x] With Bo Girds set to win week 11 and beat the median, "Sim week 11" shows that result (AT-40).
- [x] Under reduced motion, no element moves its position (AT-41).
- [x] The site evidence set of each screen passes the overlap check at the four sizes.
- [x] `make check-fast` passes.

## Comments

Closes with the squash merge of the spec PR: `season-sim-07` (`71bc5351`) merged into `season-sim` as `5ff29df5`; fix `4c485cd8` fixed AT-41, the replay under reduced motion on 2026-11-18.
AT-38 to AT-41 have PASS in `.scratch/season-sim/VERDICTS.md`.
The builder did not count the files it read; the ticket commits changed 13 files, and the main ones are: packages/sim/site/page/sim-page.tsx, packages/sim/site/page/use-what-if.ts, packages/sim/site/stage/bracket.tsx, packages/sim/site/stage/pick.ts, packages/sim/site/stage/sim-stage.tsx, packages/sim/site/stage/standings.tsx, packages/sim/site/stage/steps.ts, packages/sim/README.md.
