# 01: Each build writes the full week before into the history

Spec: `.scratch/transaction-history/PRD.md`. Acceptance tests AT-4, AT-5, and AT-6.

**App:** pipeline

**What to build:** After the weekly build saves week N to the history, it copies the full transactions of week N−1, which it already fetched as `transactions_prev.json`, over the history of week N−1. So each stored week is complete one build after it ends, and the waiver board reads every won claim with no change.

**Blocked by:** none.

**Status:** ready-for-agent

- [ ] A test of the history module shows that a short `transactions.json` of week N−1 becomes the full list from `transactions_prev.json` of week N.
- [ ] A test shows that with no `transactions_prev.json`, or with no history of week N−1, the history stays byte for byte the same and no error rises. A week 1 build writes nothing.
- [ ] A test shows that when the history write raises an `OSError`, the build logs "not saved to history" and still writes `page.json`.
- [ ] The copy is a file copy, not a symlink, and it is atomic.
- [ ] A run of the history step of the week 8 build on a temporary copy of the CPC files turns a 32-row week 7 into 59 rows.
- [ ] The loader keeps its swap of fresh transactions, and the live path does not change.
