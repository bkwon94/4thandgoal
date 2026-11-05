# 01: The grade ranks by season points per game

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests AT-9 and AT-32.

**App:** pipeline

**What to build:** Inside a grade, the Position rank sorts each player by his season points per game, over the games he played. One big game no longer moves a player about 40 spots: Omar Cooper Jr. reads as WR26 through week 8, not WR18. The grade, the finder, roster fit, and the best lineup of the grade read the season measure. The weekly report and the manager grade keep the 4-week measure and give the same ranks as before.

**Blocked by:** None. It can start now.

**Status:** ready-for-agent

- [x] The `league` package gives the season measure next to the 4-week measure. The due-back step and the out-for-season step still apply to both.
- [ ] A real `2026` week 9 grade reads Cooper (`13276`) as WR26 at the Position rank.
- [ ] `make -C apps/pipeline build WEEK=8` gives the same Position ranks in `page.json` on this branch and on `main`.
- [x] The manager grade gives the same ranks as on `main`.
- [x] `GLOSSARY.md` says that "Lineup value" and "Position rank" read season points per game inside the grade.
- [x] `make check-fast` passes at the root.
