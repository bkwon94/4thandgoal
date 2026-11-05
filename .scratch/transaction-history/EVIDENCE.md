# Transaction history: evidence

Spec: `.scratch/transaction-history/PRD.md`. Acceptance tests: `.scratch/transaction-history/ACCEPTANCE.md`.
Built from: `a818d636`, on 2026-11-05. The agent gives no Test verdict. Brian gives one for each test.

## AT-1: The backfill completes CPC week 6

App: pipeline
Then: the file holds 83 rows, and its transaction IDs equal the IDs of the live leg 6.
Files: `evidence/AT-1/output.txt`
Observation: The file holds 83 rows, and the live leg 6 holds 83 rows. The sorted diff of the transaction IDs has no lines.

## AT-2: The backfill completes CPC week 7

App: pipeline
Then: the file holds 59 rows, and its transaction IDs equal the IDs of the live leg 7.
Files: `evidence/AT-2/output.txt`
Observation: The file holds 59 rows, and the live leg 7 holds 59 rows. The sorted diff of the transaction IDs has no lines.

## AT-3: The waiver board reads every won claim

App: pipeline
Then: the spec branch returns 100 won claims, and `main` returns 77.
Files: `evidence/AT-3/output.txt`
Observation: On the spec branch, `bid_history` for CPC at week 8 returns 222 claims and 100 won. With the history files of `main`, it returns 162 claims and 77 won.

## AT-4: A build writes the full week before

App: pipeline
Then: `history/week-07/transactions.json` of the copy holds 59 rows, equal to `week-08/raw/transactions_prev.json`.
Files: `evidence/AT-4/output.txt`
Observation: On a copy of the CPC data, the history step turns the week 7 file from 32 rows into 59 rows. `cmp` shows the file is identical to `week-08/raw/transactions_prev.json`. The five tests of the history step pass.

## AT-5: A missing source leaves the history as it is

App: pipeline
Then: `history/week-07/transactions.json` of the copy is byte for byte the same as before, and the step raises no error.
Files: `evidence/AT-5/output.txt`
Observation: With `transactions_prev.json` removed, the week 7 file keeps 32 rows and the same checksum `8167a8b224cd85bc` before and after. The step exits with 0.

## AT-6: A failed write does not stop the build

App: pipeline
Then: the build logs the warning "not saved to history" for the week, and it still writes `page.json`.
Files: `evidence/AT-6/output.txt`
Observation: The test makes the history of week 5 read-only and builds week 6. The log shows "week 5 not saved to history: [Errno 13] Permission denied", and the test, which checks that `page.json` exists, passes.

## AT-7: Out of scope: no published page changes

App: pipeline
Then: the diff lists no file under `clients/*/published/`, no file under `clients/norcal/`, and no change to the live path in `packages/league/python/src/league/live.py`.
Files: `evidence/AT-7/output.txt`
Observation: The diff lists 11 files. The only data files are the CPC history of weeks 6 and 7. A filter on `clients/norcal`, `clients/*/published`, and `live.py` lists 0 files.
