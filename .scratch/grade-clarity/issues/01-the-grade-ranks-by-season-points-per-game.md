# 01: The grade ranks by season points per game

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests AT-9 and AT-32.

**App:** pipeline

**What to build:** Inside a grade, the Position rank sorts each player by his season points per game, over the games he played. One big game no longer moves a player about 40 spots: Omar Cooper Jr. reads as WR26 through week 8, not WR18. The grade, the finder, roster fit, and the best lineup of the grade read the season measure. The weekly report and the manager grade keep the 4-week measure and give the same ranks as before.

**Blocked by:** None. It can start now.

**Status:** done

- [x] The `league` package gives the season measure next to the 4-week measure. The due-back step and the out-for-season step still apply to both.
- [ ] A real `2026` week 9 grade reads Cooper (`13276`) as WR26 at the Position rank.
- [ ] `make -C apps/pipeline build WEEK=8` gives the same Position ranks in `page.json` on this branch and on `main`.
- [x] The manager grade gives the same ranks as on `main`.
- [x] `GLOSSARY.md` says that "Lineup value" and "Position rank" read season points per game inside the grade.
- [x] `make check-fast` passes at the root.

## Comments

- The merge: `9f1e253` into `grade-clarity` on 2026-11-05. `make check BASE=main` passed.
- Box 2 stays open: the grade ranks Cooper WR27, not WR26. The due-back step puts A.J. Brown, 10.77 a game by his projection ahead, one place above Cooper at 10.70. The research script of decision 01 left that step out. AT-9 names WR26, so Brian decides it in the Test verdict.
- Box 3 stays open: the agent ran no `make build WEEK=8`. `week_snapshot` gives the same rank table, lineup values, and manager grades as `main` for weeks 6, 7, and 8. The evidence stage runs the build for AT-32.
