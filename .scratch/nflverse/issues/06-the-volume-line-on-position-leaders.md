# 06 — The volume line on position leaders

Spec: `.scratch/nflverse/PRD.md`.

**What to build:** Each position leader carries a volume fact beside his points: WOPR for a WR or TE, carry
share for an RB, none for a QB, K, or DEF. The fact holds the week N number and the leader's rank on it at
his position, league wide across every started player. The position leaders chapter may cite it, so the
writer can say "first among tight ends on WOPR" as a fact.

**Blocked by:** 02 The nflverse weekly player file.

**Status:** ready-for-agent

- [ ] A WR leader's fact holds his WOPR and his WOPR rank among the started WRs of the week.
- [ ] An RB leader's fact holds his carry share and his rank among the started RBs.
- [ ] A QB leader has no volume fact.
- [ ] A leader with no usage row has no volume fact, and the chapter builds without it.
- [ ] The position leaders chapter may cite the facts and no other chapter may.
- [ ] Every number in each fact's text is in its numbers.
