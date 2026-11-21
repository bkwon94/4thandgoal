# 01: The Trade block on the find route

Spec: `.scratch/trade-block/PRD.md`. Acceptance tests AT-1, AT-3, AT-4, AT-5, AT-6, AT-7, and AT-8.

**App:** both

**What to build:** A caller of the find route can send a Trade block of 0 to 3 players of the asker's roster, and each offer of the search sends at least one of them. A bad block gets a 422 with a plain reason. A search with a block never serves the cached list of a search without one, and it reads the Fair cache like any press.

**Blocked by:** none

**Status:** in-review

- [x] The find request takes an optional `trade_block` of 0 to 3 ids, and an empty or missing block keeps every offer as now.
- [x] The route rejects 4 ids, a repeated id, and a player of another roster with a 422 and a plain reason.
- [x] The Value screen keeps only offers whose asker side sends at least one block player, and a package of two block players passes.
- [x] A block player who fails the pool rules enters no offer and raises no error, and the other block players still get offers.
- [x] The finder cache key holds the sorted block, and the Fair cache key does not change.
- [x] A press on the local evidence API after the warm-up, with Walker on the block, logs 0 new fair asks.
- [x] The glossary entry of the Partner filter matches the code: the Spares tree runs with an anchor and with a block too.
- [ ] `make check-fast` passes, and the full analyzer and API suites pass at the merge.
