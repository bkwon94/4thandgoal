# 01: The Trade block on the find route

Spec: `.scratch/trade-block/PRD.md`. Acceptance tests AT-1, AT-3, AT-4, AT-5, AT-6, AT-7, and AT-8.

**App:** both

**What to build:** A caller of the find route can send a Trade block of 0 to 3 players of the asker's roster, and each offer of the search sends at least one of them. A bad block gets a 422 with a plain reason. A search with a block never serves the cached list of a search without one, and it reads the Fair cache like any press.

**Blocked by:** none

**Status:** done

- [x] The find request takes an optional `trade_block` of 0 to 3 ids, and an empty or missing block keeps every offer as now.
- [x] The route rejects 4 ids, a repeated id, and a player of another roster with a 422 and a plain reason.
- [x] The Value screen keeps only offers whose asker side sends at least one block player, and a package of two block players passes.
- [x] A block player who fails the pool rules enters no offer and raises no error, and the other block players still get offers.
- [x] The finder cache key holds the sorted block, and the Fair cache key does not change.
- [x] A press on the local evidence API after the warm-up, with Walker on the block, logs 0 new fair asks.
- [x] The glossary entry of the Partner filter matches the code: the Spares tree runs with an anchor and with a block too.
- [x] `make check-fast` passes, and the full analyzer and API suites pass at the merge.

## Comments

The merge: `13827a32` on `trade-block-01`, merged into `trade-block` on 2026-11-21.
The proof: The full check of the Spec branch passed on 2026-11-21, with 1911 site unit tests and 1757 pipeline tests, and the Judge gave PASS to all 32 acceptance tests. AT-1, AT-3 to AT-8 show the block rule, the 422 reasons, the cache key, and 0 new fair asks on the local evidence API, with Cam Skattebo as the stand-in for Walker.
Read at least 12 files: AGENTS.md, apps/pipeline/AGENTS.md, .scratch/trade-block/PRD.md, .scratch/trade-block/ACCEPTANCE.md, .scratch/trade-block/issues/01-the-trade-block-on-the-find-route.md, GLOSSARY.md, packages/analyzer/python/src/analyzer/finder_search.py, packages/analyzer/python/src/analyzer/routes.py, packages/analyzer/python/src/analyzer/cache.py, apps/pipeline/tests/test_finder_search.py, apps/pipeline/tests/test_fair_cache.py, apps/api/tests/test_api.py.
Closes with the squash merge of the spec PR.
