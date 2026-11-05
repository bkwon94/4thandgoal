# 03: The Season rank and the Recent rank

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests AT-6, AT-7, AT-8, and AT-31.

**App:** both

**What to build:** Each player in a grade shows his Season rank, such as WR60, as Sleeper sorts it. A Recent rank shows beside it, with its label, only when the two differ by 12 spots or more. No text says "takes RB1" or "sits on the bench". The finder facts use the same ranks.

**Blocked by:** 02.

**Status:** ready-for-agent

- [ ] `RECENT_RANK_GAP = 12` is in the analyzer tunables.
- [ ] Each player of `trade.sides` carries `season_rank`, and `recent_rank` when the gap holds, else null.
- [ ] In a real `2026` week 9 grade, Cooper (`13276`) has `season_rank` WR60 and `recent_rank` WR18.
- [ ] The facts of a traded player give the Season rank, and the Recent rank with its label when the gap holds. They give no Position rank number.
- [ ] The slot fact is gone from the fact sheet of the grade and of the finder.
- [ ] The side card shows the Season rank of each player, and the Recent rank only when it is present.
- [ ] `make check-fast` passes at the root.
