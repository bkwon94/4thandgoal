# 02: The front door gives ask uses the block

Spec: `.scratch/trade-block/PRD.md`. Acceptance tests AT-28 and AT-29.

**App:** both

**What to build:** In the front door chat, "What can I get for Walker?" finds trades through a Trade block of one player. "How do I get Bijan Robinson?" works as it does now, through the anchor with the side "gets".

**Blocked by:** 01

**Status:** done

- [x] A "gives" ask sends `trade_block` with the one player id and no anchor.
- [x] A "gets" ask sends the anchor with the side "gets" and no `trade_block`.
- [x] The side "gives" of the anchor retires from the find route, and no caller sends it.
- [x] `make check-fast` passes, and the full API suite passes at the merge.

## Comments

The merge: `b38702d5` on `trade-block-02`, merged into `trade-block` on 2026-11-21.
The proof: The full check of the Spec branch passed on 2026-11-21, with 1911 site unit tests and 1757 pipeline tests, and the Judge gave PASS to all 32 acceptance tests. AT-28 and AT-29 print the find request of each ask: a block of one for "gives", and the anchor with no block for "gets".
Read at least 10 files: AGENTS.md, .scratch/trade-block/PRD.md, .scratch/trade-block/ACCEPTANCE.md, .scratch/trade-block/issues/02-the-front-door-gives-ask-uses-the-block.md, apps/api/src/cornerstone_api/trade_topics.py, packages/analyzer/python/src/analyzer/finder_search.py, packages/analyzer/python/src/analyzer/routes.py, apps/api/tests/test_trade_topics.py, apps/api/tests/test_api.py, apps/pipeline/tests/test_finder_search.py.
Closes with the squash merge of the spec PR.
