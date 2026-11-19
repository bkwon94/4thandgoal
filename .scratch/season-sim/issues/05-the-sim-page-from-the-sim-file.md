# 05: The sim page from the sim file, and the menu item

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests AT-24 to AT-32, AT-37, AT-50, AT-63, and AT-65. Decision 04, layout D "Cards".

**App:** site

**What to build:** Each client that takes the sim package has a page at `/sim/<season>/`. It reads the latest `week-NN/sim.json` and opens on Your team: the header with the avatar, the name, the record, the weeks left, and the playoff odds, then the sentence of more wins, which opens the ladder. A week switch goes from the current week to week 14, then Playoffs. Each week page holds the week card with its result tiles and the root-for card. On a phone, the root-for card opens from one row. From tablet width up, it always shows. A number with the "about" flag reads "about X%". The page makes no API call in this ticket. The menu gets "Season sim". The design follows the prototype in `~/plans/season-sim-prototype/final/`, and meets the design bar of each UI ticket. The copy never says "rival", "Brian", or an internal name.

**Blocked by:** 03.

**Status:** ready-for-agent

- [x] The `cpc` page with Bo Girds shows the header of AT-24, and the sentence opens the ladder of the file (AT-25).
- [x] The week switch has Wk 11 to Wk 14 and Playoffs, and each opens its week page (AT-26).
- [x] Week 11 in `cpc` shows four tiles against Maye d'force B with U (AT-27), and in `norcal` two tiles against The Mean Machine (AT-28).
- [x] The root-for card says "If you lose, you drop to X%", with "→ Y%" on each row (AT-29), opens from one row at 390x660, and shows in full at 1080x740 (AT-30).
- [x] "Maye d'force B with U" shows with no cut word in a root-for row at 390x660 (AT-31), and a flagged number reads "about X%" (AT-32).
- [x] The page makes no What-if call on load or on a switch of weeks (AT-37), and no site module draws a score (AT-63).
- [x] The only result tiles are those of Your team, and no grid lists every game (AT-65).
- [x] The menu has "Season sim", and it opens `/sim/2026/` (AT-50).
- [x] The site evidence set passes the overlap check at 390x660, 810x980, 1080x740, and 1280x800, light and dark.
- [x] `make check-fast` passes.
