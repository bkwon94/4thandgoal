# 02: The front door gives ask uses the block

Spec: `.scratch/trade-block/PRD.md`. Acceptance tests AT-28 and AT-29.

**App:** both

**What to build:** In the front door chat, "What can I get for Walker?" finds trades through a Trade block of one player. "How do I get Bijan Robinson?" works as it does now, through the anchor with the side "gets".

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] A "gives" ask sends `trade_block` with the one player id and no anchor.
- [ ] A "gets" ask sends the anchor with the side "gets" and no `trade_block`.
- [ ] The side "gives" of the anchor retires from the find route, and no caller sends it.
- [ ] `make check-fast` passes, and the full API suite passes at the merge.
