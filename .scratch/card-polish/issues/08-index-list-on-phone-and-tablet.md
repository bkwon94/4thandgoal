# 08: Index list on phone and tablet

Spec: `.scratch/card-polish/PRD.md`. Acceptance tests AT-9, AT-22, AT-23, AT-24, and AT-26.

**App:** site

**What to build:** The Managers index becomes a ledger of the teams in power-ranking order, after the Team Roster item. Each row shows the place, a small avatar, the team name, and the playoff odds. Chips All, In, Bubble, and Out filter the ledger, each with its count. A tap opens a row in place with the Open card drawer: the letter, the grade read, the four arcs of the Grade dial, and a link to the manager page. One row is open at a time, and the name of the open row rolls its letters. The grid of manager cards goes. Both clients work.

**Blocked by:** 01 and 04

**Status:** ready-for-agent

- [ ] CPC week 8 shows all 12 rows on one 390 px screen, with the chips All 12, In 6, Bubble 2, and Out 4.
- [x] A tap on Bubble shows only Teehee and Return of T Mac.
- [x] A tap on The Blue Tent opens it with A and four arcs, and a tap on Lil Fridge closes it and opens Lil Fridge.
- [x] A unit test of the race group covers clinched, eliminated, 75%, and 25%.
- [x] The NorCal index shows In 4, Bubble 5, and Out 3.
- [x] The reduced-motion test proves a row opens at once.
- [x] `make check-fast` passes.
