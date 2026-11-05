# Transaction history: acceptance tests

Spec: `.scratch/transaction-history/PRD.md`.

The Test verdict: only Brian gives one. He writes one PR comment on the Spec branch PR, with one line for each test: the id, then PASS, FAIL, or BLOCKED, then an optional note. The PR merges when every test has PASS (ADR 0020). An agent records the evidence and gives no Test verdict.

## Tests

AT-1: The backfill completes CPC week 6
App: pipeline
Stories: 1, 8
Given: CPC 2026, with the backfill on the spec branch.
When: the reader counts the rows of `clients/cpc/data/2026/history/week-06/transactions.json` and compares them to `https://api.sleeper.app/v1/league/1386167364424318976/transactions/6`.
Then: the file holds 83 rows, and its transaction IDs equal the IDs of the live leg 6.
Evidence: the `jq length` output of the file, and a sorted diff of the transaction IDs of the file and the live leg, with no lines.

AT-2: The backfill completes CPC week 7
App: pipeline
Stories: 1, 8
Given: CPC 2026, with the backfill on the spec branch.
When: the reader counts the rows of `clients/cpc/data/2026/history/week-07/transactions.json` and compares them to `https://api.sleeper.app/v1/league/1386167364424318976/transactions/7`.
Then: the file holds 59 rows, and its transaction IDs equal the IDs of the live leg 7.
Evidence: the `jq length` output of the file, and a sorted diff of the transaction IDs of the file and the live leg, with no lines.

AT-3: The waiver board reads every won claim
App: pipeline
Stories: 1, 2, 3
Given: CPC 2026 week 8, with the backfill on the spec branch.
When: the reader runs `bid_history` for CPC at week 8 on the spec branch, and again on `main`.
Then: the spec branch returns 100 won claims, and `main` returns 77.
Evidence: the command and its output on both branches: the count of all claims and the count of won claims.

AT-4: A build writes the full week before
App: pipeline
Stories: 5, 6, 7, 12, 13, 14
Given: a copy of the CPC 2026 data in a temporary folder, with `history/week-07/transactions.json` from `main` (32 rows) and `week-08/raw/transactions_prev.json` (59 rows).
When: the reader runs the history step of the week 8 build on the copy.
Then: `history/week-07/transactions.json` of the copy holds 59 rows, equal to `week-08/raw/transactions_prev.json`.
Evidence: the command, the row count before and after, and the output of the new test of the history module.

AT-5: A missing source leaves the history as it is
App: pipeline
Stories: 16
Given: a copy of the CPC 2026 data in a temporary folder, with `week-08/raw/transactions_prev.json` removed.
When: the reader runs the history step of the week 8 build on the copy.
Then: `history/week-07/transactions.json` of the copy is byte for byte the same as before, and the step raises no error.
Evidence: the command, the checksum of the file before and after, and the output of the new test of the history module.

AT-6: A failed write does not stop the build
App: pipeline
Stories: 10
Given: a build of a week in which the history write raises an `OSError`.
When: the build runs.
Then: the build logs the warning "not saved to history" for the week, and it still writes `page.json`.
Evidence: the output of the test that proves it, with the logged warning.

AT-7: Out of scope: no published page changes
App: pipeline
Stories: none
Given: the spec branch `transaction-history`.
When: the reader runs `git diff --stat main...transaction-history`.
Then: the diff lists no file under `clients/*/published/`, no file under `clients/norcal/`, and no change to the live path in `packages/league/python/src/league/live.py`.
Evidence: the full `git diff --stat` output.

## Trace

Story 1: AT-1, AT-2, AT-3
Story 2: AT-3
Story 3: AT-3
Story 4: AT-7. The diff shows NorCal data unchanged. A NorCal build after the merge proves the fix there.
Story 5: AT-4
Story 6: AT-4
Story 7: AT-4
Story 8: AT-1, AT-2
Story 9: AT-1, AT-2
Story 10: AT-6
Story 11: no test. Reason: the publish rule already allows `clients/<slug>/data/<season>/`, and no publish code changes.
Story 12: AT-4
Story 13: AT-4
Story 14: AT-4
Story 15: no test. Reason: the spec does not change the loader, and its tests stay as they are.
Story 16: AT-5
Out of scope "A rebuild of the week 8 waiver board or of `managers.json`": AT-7
Out of scope "A change to the live path": AT-7
Out of scope "A fetch of the week 8 leg now": AT-7

## Revisions

None yet.
