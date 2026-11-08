# 03: Award and trade cards on the Open card

Spec: `.scratch/card-polish/PRD.md`. Acceptance tests AT-7.

**App:** site

**What to build:** AwardTile and TradeCard on the week page open and close with the Open card, with a head of their own and chips from the fields they show now.

**Blocked by:** 01

**Status:** wontfix

- [x] Each AwardTile and each TradeCard of CPC week 8 opens with the same drawer, blur-in, and chevron as the game card.
- [x] Part tests prove the toggle states of both cards.
- [x] `make check-fast` passes.

## Comments

- 2026-11-08: wontfix. Brian checked the build on his phone. The award panel held only the team and the projection, and the trade card moved its manager links into the panel. The cards go back to their plain look, and AT-7 is retired.
