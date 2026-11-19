# 10: The Announcement

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests AT-51 to AT-61. Decision 05.

**App:** site

**What to build:** The Announcement is a general component on the shared Sheet, with an art slot, an eyebrow, a title, one line, the link, and "Not now". The site name comes in as a prop. The sim is its first use: the art shows the playoff odds of Your team and three standings rows around it with the playoff line, and a What-if chip that the manager can tap. The chip turns on once by itself after the sheet settles. The Announcement opens about 0.7 s after page load. It does not open while another sheet is open, on the sim page, or while no team is set. A dismiss or a press of the link hides it for good in this browser. A skipped open does not count. It stops 1 week after the release. The prototype is in `~/plans/season-sim-prototype/announcement/`.

**Blocked by:** 05.

**Status:** done

- [x] A fresh browser with Bo Girds opens the sheet with The Blue Tent, Bo Girds, and Return of T Mac, the playoff line, the chip, and the copy of the spec (AT-51).
- [x] The chip turns off and on with a tap (AT-52), and turns on once by itself after the sheet stops (AT-53).
- [x] A drag down, "Not now", Escape, and a tap on the dim each close it (AT-54).
- [x] A dismiss or a press of the link hides it on a reload (AT-55).
- [x] It does not open on `/sim/2026/` or over the menu sheet (AT-56).
- [x] A first visit shows only the team picker, and the next load shows the Announcement (AT-57). With no team set, it does not open (AT-58).
- [x] It does not open 1 day past its end date (AT-59).
- [x] The component renders a test art slot and test copy with the same close rules (AT-60).
- [x] Under reduced motion, the rows and the odds show at once, and the chip does not turn on by itself (AT-61).
- [x] The site evidence set passes the overlap check at the four sizes.
- [x] `make check-fast` passes.

## Comments

Closes with the squash merge of the spec PR: `season-sim-10` (`6fa17ec5`) merged into `season-sim` as `3bf34857`; fix `b5de9120` made the Announcement skip the load of the team picker on 2026-11-18.
AT-51 to AT-61 have PASS in `.scratch/season-sim/VERDICTS.md`.
The builder did not count the files it read; the ticket commits changed 16 files, and the main ones are: apps/site/scripts/client-build.mjs, apps/site/src/app/_routes/sim/announcement.tsx, apps/site/src/app/_routes/sim/home-banner.tsx, apps/site/src/app/use-announcement.ts, apps/site/src/lib/client-values.ts, packages/design/site/parts/announcement.tsx, packages/sim/site/announcement/preview.ts, packages/sim/site/announcement/sim-preview.tsx.
