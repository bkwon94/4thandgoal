# 04: The cards spread across the block

Spec: `.scratch/trade-block/PRD.md`. Acceptance tests AT-2, AT-9, AT-11, and AT-14.

**App:** both

**What to build:** With two or three players on the Trade block, the cards spread across them: each block player with a fair offer on the Shortlist gets at least one card. When no fair trade sends a block player, the page says so and names the block players.

**Blocked by:** 01

**Status:** done

- [x] When the block is not empty, the tier of `varied` for the players that the asker gives counts only block players.
- [x] The user message of the pick names the block players, and the prompt holds the rule that a block player with a fair Shortlist offer gets at least one pick.
- [x] A real press with Walker and Flowers on the block gives at least one card for each of them that has a fair Shortlist offer.
- [x] An empty answer of a block search carries the line "No fair trade sends Walker or Flowers with the partner and the position you picked.", with the names of the block.
- [x] `make check-fast` passes, and the full analyzer suite passes at the merge.

## Comments

The merge: `3ed8ae49` on `trade-block-04`, merged into `trade-block` on 2026-11-21.
The proof: The full check of the Spec branch passed on 2026-11-21, with 1911 site unit tests and 1757 pipeline tests, and the Judge gave PASS to all 32 acceptance tests. AT-2, AT-9, AT-11, and AT-14 show the spread on the Shortlist, the block line of the pick, and the empty line with the block names.
Read at least 10 files: AGENTS.md, apps/pipeline/AGENTS.md, .scratch/trade-block/PRD.md, .scratch/trade-block/ACCEPTANCE.md, .scratch/trade-block/issues/04-the-cards-spread-across-the-block.md, packages/analyzer/python/src/analyzer/finder_search.py, packages/analyzer/python/src/analyzer/finder_pick.py, packages/analyzer/python/src/analyzer/prompts/finder_pick.md, apps/pipeline/tests/test_finder_search.py, apps/api/tests/test_api.py.
Closes with the squash merge of the spec PR.
