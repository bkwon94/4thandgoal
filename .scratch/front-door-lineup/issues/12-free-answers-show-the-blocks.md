# 12: Free answers show the blocks, with the transaction feed

Spec: `.scratch/front-door-lineup/PRD.md`. Acceptance tests AT-35.

**App:** both

**What to build:** A free answer may show any of the fifteen blocks. A question about league moves gets the transaction feed: a strip of the moves per day, one row per move newest first with a dot for its kind, and a trade row that shows what each side got.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] "What moves happened this week?" in cpc gives a free answer with the transaction feed (AT-35).
- [x] A pytest shows that the free answer accepts each of the fifteen kinds.
- [ ] Site screenshots show the feed.
