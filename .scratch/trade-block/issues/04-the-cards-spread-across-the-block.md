# 04: The cards spread across the block

Spec: `.scratch/trade-block/PRD.md`. Acceptance tests AT-2, AT-9, AT-11, and AT-14.

**App:** both

**What to build:** With two or three players on the Trade block, the cards spread across them: each block player with a fair offer on the Shortlist gets at least one card. When no fair trade sends a block player, the page says so and names the block players.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] When the block is not empty, the tier of `varied` for the players that the asker gives counts only block players.
- [x] The user message of the pick names the block players, and the prompt holds the rule that a block player with a fair Shortlist offer gets at least one pick.
- [ ] A real press with Walker and Flowers on the block gives at least one card for each of them that has a fair Shortlist offer.
- [x] An empty answer of a block search carries the line "No fair trade sends Walker or Flowers with the partner and the position you picked.", with the names of the block.
- [ ] `make check-fast` passes, and the full analyzer suite passes at the merge.
