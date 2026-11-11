# 02: The backfill of CPC weeks 6 and 7

Spec: `.scratch/transaction-history/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, and AT-7.

**App:** pipeline

**What to build:** The two short CPC history files of weeks 6 and 7 hold every transaction of their week, copied from the `transactions_prev.json` that the builds of weeks 7 and 8 saved. Then the bid history of CPC at week 8 reads every won claim.

**Blocked by:** none.

**Status:** done

- [x] The CPC history of week 6 holds 83 rows, and its transaction IDs equal the live leg 6.
- [x] The CPC history of week 7 holds 59 rows, and its transaction IDs equal the live leg 7.
- [x] The bid history of CPC at week 8 returns 100 won claims on the spec branch, against 77 on `main`.
- [x] No file under `clients/*/published/` and no file under `clients/norcal/` changes.
- [x] No week 8 leg is fetched. The week 9 build writes it through ticket 01.

## Comments
- Closed by the merge of PR #10.
