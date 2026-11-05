# 12: Why is the stored transaction history incomplete, and where does the fix go?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The stored CPC history misses transactions. Week 6 holds 44 of 83 rows, week 7 holds 32 of 59, and week 8 holds 15 of 42, against the live `/league/{id}/transactions/{week}`. Ticket 01 found that the repo swaps in `transactions_prev.json` for weeks 1 to 7. Brian wants the gap fixed in this spec. The spec needs the cause, which pages the gap changes, such as the trades and waiver facts of the weekly page, and the seam of the fix. Write the notes at `decisions/12-research-transaction-history-gap.notes.md`.

## Decision

The research found the cause, and Brian moved the fix to its own spec on 2026-11-05. The notes are `decisions/12-research-transaction-history-gap.notes.md`.

- The Tuesday build saves week N to the history before the Wednesday waiver run, and nothing writes the full week back. The week 8 waiver board read 77 of 100 won claims.
- The fix and the backfill are a separate spec, `transaction-history`, so they ship before the week 9 build on 2026-11-10. This spec does not depend on it: the report fetches the transactions of each week again.
