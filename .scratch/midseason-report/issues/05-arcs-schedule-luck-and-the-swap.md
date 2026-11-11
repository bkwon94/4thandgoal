# 05: Arcs, Schedule luck, and the schedule swap

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests AT-5, AT-6, and AT-7.

**App:** pipeline

**What to build:** `midseason.json` holds the arcs of each team, Schedule luck with All-play wins, points against, and the close-game record, and the 12 by 12 schedule swap with its two callouts. The rules are those of tickets 05 and 06 of `decisions/`.

**Blocked by:** 01 and 02.

**Status:** done

- [x] Return of T Mac has Roller coaster and Turnaround and no third arc. Bo Girds has Snakebit and Collapse.
- [x] All You Need Is Love has +2.73 Schedule luck, and Bo Girds has -2.18.
- [x] The diagonal of the swap equals the standings, and Bo Girds with the schedule of Maye d'force B with U is 14-2.
- [x] Rule tests cover a tie as half a win, the self-meet rule, and the 2-arc limit.

## Comments
- Closed by the merge of PR #13.
