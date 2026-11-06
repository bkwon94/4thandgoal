# Transaction history: the history keeps every transaction of each week

Status: ready-for-agent
Date: 2026-11-05
Apps: pipeline. Each weekly build writes the full transactions of the week before into the history, and CPC weeks 6 and 7 get a backfill. The site does not change.
Spec branch: `transaction-history`.
Source: the session of 2026-11-05, and decision ticket 12 of the midseason report, with its notes `.scratch/midseason-report/decisions/12-research-transaction-history-gap.notes.md` on the spec branch `midseason-report`.
Tickets: 01 to 02, in `issues/`.

## Problem Statement

The waiver board tells a manager what to bid. Its bid advice reads the won claims of past weeks from the stored history. The stored history misses most of the claims of each week, so the advice reads too few claims and bids too low.

The week 8 board of CPC read 77 of the 100 won claims. Its last-like claim was wrong at every position, and 21 of its 24 bids were too low. For example, player 8254, a running back, showed $4, and the full history gives $16.

The cause is the order of two events. The week N build runs on Tuesday and saves the transactions of week N into the history. Sleeper runs the waivers on Wednesday at 03:09 ET, after the build. No step writes the full week back. CPC weeks 6, 7, and 8 hold 44 of 83, 32 of 59, and 15 of 42 rows. NorCal is complete now only because its week 8 build ran late. Its next Tuesday build starts the same gap.

The trades and `managers.json` are correct today, because their loader swaps in a fresh copy of each week. The waiver board does not swap, and each new reader of the history must know the swap or be wrong.

## Solution

Each weekly build writes the full transactions of week N−1 into the history. The build already fetches that week as `transactions_prev.json`, and Sleeper has closed it by the Tuesday build, so the fix needs no new call to Sleeper. After the fix, each stored week is complete one build after it ends.

The spec also backfills CPC weeks 6 and 7 from the saved `transactions_prev.json` files, which match the live API row for row. The week 9 build writes week 8 through the fix. NorCal needs no backfill.

No published page is rebuilt. The week 8 waiver run is over, so the week 9 board is the first to read the full history.

## User Stories

1. As a manager, I want the waiver board to read every won claim of the season, so that its bid advice is not too low.
2. As a manager, I want the last-like claim of each position to be the real latest claim, so that the floor of a bid matches what the league paid.
3. As a manager, I want the week 9 board to be right, so that I do not lose a player to a bid that the board told me was enough.
4. As a NorCal manager, I want my league to keep a complete history, so that my board never gets the CPC gap.
5. As Brian, I want each stored week to be complete one build after it ends, so that I can trust the files under `history/`.
6. As Brian, I want the fix to need no new call to Sleeper, so that a build makes no more requests than today.
7. As Brian, I want the fix to happen in the build that already runs each week, so that I run no new command.
8. As Brian, I want CPC weeks 6 and 7 backfilled in this spec, so that the week 9 board reads a complete season.
9. As Brian, I want the backfill to come from the saved files, so that it matches what the builds saw and needs no fetch.
10. As Brian, I want a failure of the history write to log a warning and not stop the build, so that a page still publishes.
11. As Brian, I want the weekly `publish` to ship the rewritten history file, so that the next build reads it.
12. As an agent who adds a reader of the history, I want the stored files to be complete, so that I need not know about a swap.
13. As an agent, I want a test that proves the build writes the full week N−1, so that a later change cannot bring the gap back.
14. As the midseason report, I want the stored history to be complete, so that a later version can read it with no refetch.
15. As Brian, I want the swap in the loader to stay, so that a week whose next raw directory exists still reads fresh data.
16. As Brian, I want a missing `transactions_prev.json` to leave the history as it is, so that a first week or an old week does not fail.

## Implementation Decisions

- The history module gets one function beside `save_week_to_history`. It copies `transactions_prev.json` of the raw directory of week N over the `transactions.json` of the history of week N−1. It does nothing when either the source file or the history week is missing.
- The weekly build calls it right after `save_week_to_history`, in the same guard. A failure logs a warning, and the page still publishes.
- The copy is a copy, not a symlink, and is atomic, for the same reason as the rest of the history: a refetch of the raw directory must not change the history.
- The loader keeps its swap of fresh transactions. It still covers a week whose history copy is old.
- The waiver board needs no change. It reads the complete files.
- The live path, which writes the history from memory, does not change. The next weekly build overwrites its week with the full copy.
- The backfill copies CPC `week-07/raw/transactions_prev.json` to the history of week 6, and `week-08/raw/transactions_prev.json` to the history of week 7. The spec PR commits the two data files.
- Week 1 has no week 0, so a week 1 build writes nothing.

## Testing Decisions

- A good test checks the files that the build leaves on disk, not the calls inside it.
- The seam is the history module: a test builds a raw directory of week N with a `transactions_prev.json` and a history of week N−1 with a short `transactions.json`. It runs the new function and checks that the history of week N−1 now holds the full list.
- More tests on the same seam: no source file leaves the history as it is; no history week of N−1 creates nothing; week 1 writes nothing.
- The waiver price tests in `packages/waiver/python/tests/test_waiver_price.py` and the history tests in `apps/pipeline/tests/` are the prior art for fixtures on `tmp_path`.
- One check runs on the real files after the backfill: `bid_history` of CPC through week 7 reads every won claim of the live legs 1 to 7.

## Out of Scope

- A rebuild of the week 8 waiver board or of `managers.json`. The week 8 run is over, and the week 9 build corrects `managers.json`.
- A change to the live path.
- A fetch of the week 8 leg now. The week 9 build writes it through the fix.
- A change to how the waiver board prices a bid.

## Further Notes

- The week 9 build runs on Tuesday 2026-11-10, so the spec must merge before it.
- The midseason report fetches the transactions of each week again, so it does not depend on this spec.
