# 03: The grid chapters

**What to build:** A league member on a tablet or a laptop sees the card chapters in columns: three award tiles per row, two position leader cards per row, two trade cards per row with their inner columns kept, and two next week cards per row on a tablet and three on a laptop. On a phone the columns are as they are today: two award tiles and one card per row elsewhere.

**Blocked by:** 01 The type scale, the measure, and the cards

**Status:** done

- [ ] Awards: two tiles per row under 640px, three from 640px.
- [ ] Position leaders: one card per row under 640px, two from 640px.
- [ ] Trades: one card per row under 640px, two from 640px, each card with its two inner columns.
- [ ] Next week: one card per row under 640px, two from 640px, three from 1024px.
- [ ] The grid gaps come from the spacing tokens. The Must Watch tag and the reveal stagger stay.
- [ ] The awards, position leaders, trades, and next week tests pass. The typecheck, the build, and the export check pass.
- [ ] Checked with agent-browser on the week 7 report at 390 by 844, 768 by 1024, and 1280 by 800 with reduced motion on. Screenshots as `03-<chapter>-<width>.png` in the feature folder.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in a1cf4831.
Proof: The commit "Put the grid chapters in columns from the tablet tier" merged in 1fc76869 and 95d57c8d.
Read 1 file: .scratch/todoist-queue/audit.md.
