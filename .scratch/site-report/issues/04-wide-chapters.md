# 04: The wide chapters

**What to build:** A league member on a tablet or a laptop sees the matchup of the week score row with the two teams at the edges and the score centered, the all matchups rows with names that never wrap and the recap inline under its row, the median chart with readable bars across the width, and the standings rows with the rank, the record, and the points spaced by tokens. No chapter gains data. On a phone each chapter is as it is today, with the 480px fold kept.

**Blocked by:** 01 The type scale, the measure, and the cards

**Status:** done

- [ ] Matchup of the week: from 640px the score row spreads the teams to the edges with the score centered. The blurb takes the measure.
- [ ] All matchups: from 640px the rows use the width and no name wraps. The recap opens inline under its row at every tier, as today.
- [ ] Median game: from 640px the three KPI cells and the chart use the width. The bars keep their order and the dashed median line.
- [ ] Standings: from 640px the rows use the width with the columns spaced by tokens. No new columns.
- [ ] Under 640px each chapter is as it was, and the 480px fold still works on a phone.
- [ ] The matchup, all matchups, median, and standings tests pass. The typecheck, the build, and the export check pass.
- [ ] Checked with agent-browser on the week 7 report at 390 by 844, 768 by 1024, and 1280 by 800 with reduced motion on. Screenshots as `04-<chapter>-<width>.png` in the feature folder.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in e8211e22.
Proof: The commit "Spread the four wide chapters across the tablet and desktop column" merged in 7bc3743e and 95d57c8d.
Read 1 file: .scratch/todoist-queue/audit.md.
