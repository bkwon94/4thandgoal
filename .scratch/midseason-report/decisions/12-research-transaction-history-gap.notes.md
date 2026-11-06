# 12 notes: the gap in the stored transaction history

Summary: the weekly build copies leg N into `history/week-NN/` before the Wednesday waiver run, and no step writes the full leg back. The trades, the recent adds, and the managers moves read a fresh copy and lose nothing, but the waiver board reads the stale files: 21 of the 24 bids on the CPC week 8 board are low.

Calls ran on 2026-11-05 against `https://api.sleeper.app/v1/league/{id}/transactions/{leg}`, legs 1 to 9. CPC is `1386167364424318976`, NorCal is `1402948824305049600`. Sleeper `state/nfl` gives `leg: 9` now, so legs 1 to 8 are closed.

## 1. The cause

Each build asks Sleeper for two legs (`packages/league/python/src/league/provider/sleeper.py`):

- Line 225: leg N-1, saved as `week-NN/raw/transactions_prev.json` (line 240).
- Line 226: leg N, saved as `week-NN/raw/transactions.json`. Line 228 stamps `fetched.json`.

After the page renders, `save_week_to_history` copies the leg N file into `history/week-NN/` (`apps/pipeline/src/cornerstone/pipeline.py`, line 420; `packages/league/python/src/league/history.py`, lines 340 to 347).
That copy is the only write of `history/week-NN/transactions.json`. The later fresh copy of leg N lands in `week-(N+1)/raw/transactions_prev.json` and never goes into the history.
`fetch_history` cannot repair it, because it skips a week that is on disk (`history.py`, lines 52 to 54). The comment in `live.py`, line 220, says "Past weeks never change". That is false for the last leg.

The timing, CPC, all times UTC:

| Leg | Build (fetch) | Waiver run (`status_updated`) | Stored | Live | Missing rows |
| --- | --- | --- | --- | --- | --- |
| 6 | Tue 10-20, about 15:57 (no `fetched.json`; last stored row 15:55, first missing row 15:59) | Wed 10-21 07:09 | 44 | 83 | 14 waiver complete, 24 waiver failed, 1 free_agent |
| 7 | Tue 10-27 12:00 (`week-07/raw/fetched.json`) | Wed 10-28 07:09 | 32 | 59 | 9 waiver complete, 13 waiver failed, 4 free_agent, 1 trade |
| 8 | Tue 11-03 13:05 (`week-08/raw/fetched.json`) | Wed 11-04 08:09 | 15 | 42 | 10 waiver complete, 13 waiver failed, 4 free_agent |

- Every missing waiver row has `status_updated` at the waiver run, after the build. Sleeper gives no row for a pending claim, so the build sees none of them.
- Every missing free_agent row and the missing trade have `created` after the fetch. Example: trade `1420899085560340480`, rosters 4 and 10, created Tue 10-27 20:00, after the 12:00 fetch.
- League settings: `waiver_day_of_week: 2`, `daily_waivers: 0`. The run is once a week, Wednesday 03:09 ET.

Which weeks have the gap:

- CPC weeks 1 to 5: the history equals the live API, row for row. A backfill by `fetch_history` wrote them after the legs closed.
- CPC weeks 6 to 8: the weekly build wrote them, so each misses the rows after its build.
- `week-07/raw/transactions_prev.json` and `week-08/raw/transactions_prev.json` equal live legs 6 and 7, row for row.
- NorCal weeks 1 to 8: the history equals the live API. Weeks 1 to 7 came from a backfill. The week 8 build ran Wed 11-04 at 19:51 EST (`norcal/data/2026/week-08/raw/fetched.json`), after the waiver run. NorCal gets the same gap from its first Tuesday build.

## 2. The effect

The readers of the transactions, and what each one gets:

| Reader | Source | Gap? |
| --- | --- | --- |
| Trades on `page.json` | `_window_trades` (`pipeline.py`, lines 145 to 162) reads the raw leg N and `transactions_prev.json` of leg N-1 | No |
| Recent adds, `W.adds` and `.move.` facts | `load_history` then `load_saved_weeks` (`history.py`, lines 80 to 106), which swaps in `_fresh_transactions` (lines 71 to 77) | No |
| `managers.json` moves and best adds | `_season_history` (`pipeline.py`, line 453) reads `load_saved_weeks`, so weeks to N-1 swap | Only week N, until the next build |
| Analyzer snapshot | `load_saved_weeks` (`snapshot.py`, line 433). It reads stats, not moves | No |
| Waiver board price, `waiver.json` | `bid_history` (`packages/waiver/python/src/waiver/price.py`, lines 22 to 31) reads `history/week-NN/transactions.json` directly, with no swap | Yes |

Trades, checked against the published pages: no trade is missing.

- Week 6 `page.json` has 5 trades. Trade `1418300673505644544` (rosters 7 and 8, created Tue 10-20 15:55) falls after the week 6 cutoff, and the week 7 page shows it.
- The week 8 page shows trade `1420899085560340480` (rosters 4 and 10). The fresh leg 7 gave it, since the history copy lacks it.

`managers.json` (built 11-04): weeks 1 to 7 equal the live adds for each roster. Week 8 is short for 8 rosters, because the leg 8 run came after the build. Examples: roster 1 shows 3 adds, live has 5. Roster 9 shows 1, live has 3. Roster 12 shows 0, live has 1. The week 9 build fixes this through the swap.

The waiver board, `clients/cpc/published/2026/week-08/waiver.json`: this is the one published fact that is wrong.

- `bid_history` at week 8 read 162 claims, 77 won. The full legs 1 to 7 plus the raw leg 8 hold 222 claims, 100 won. It missed the runs of 10-21 and 10-28.
- `_last_like` (`price.py`, line 120) takes the latest won claim per position. It sets the floor of the bid when its week is within `FLOOR_WEEKS = 3`.
- The published `last_like` is wrong for each position on the board:

| Position | Published (player, roster, week, bid) | Full history (player, roster, week, bid, transaction) |
| --- | --- | --- |
| RB | 12529, 8, 6, $2 | 13286, 1, 7, $15, `1420854204854976512` |
| WR | 11631, 7, 7, $7 | 13301, 6, 7, $13, `1420810832861769728` |
| TE | 9480, 2, 5, $15 | 8210, 10, 7, $12, `1420906970721878016` |
| QB | 1166, 4, 6, $0 | 3257, 1, 7, $2, `1420853982535938048` |
| DEF | HOU, 10, 6, $0 | JAX, 6, 7, $6, `1420811307342401536` |

- With the full history, 21 of the 24 board bids rise. Each RB goes to $16, each WR to $14, and each TE to $13. Examples: player 11729 (RB) $11 to $16. Player 8254 (RB) $4 to $16. Player 10214 (TE) $5 to $13.
- The week 7 board has no `waiver.json` in `published/`, so week 8 is the one wrong board.
- The midseason report has the same risk if it reads `history/week-NN/transactions.json` directly.

## 3. The fix seam

The smallest fix: make the build write the fresh leg N-1 into the history, so the stored file is complete.

1. Add one function to `packages/league/python/src/league/history.py`, beside `save_week_to_history`. It copies `history_raw_dir(root, week)/transactions_prev.json` to `history_week_dir(root, week - 1)/transactions.json`, when both exist.
2. Call it in `apps/pipeline/src/cornerstone/pipeline.py`, next to `save_week_to_history` (line 420), in the same try block.
3. Keep `_fresh_transactions` in `load_saved_weeks`. It still covers a week whose next raw directory is on disk but whose history copy is old.

Why this place:

- `fetch_week` already gets leg N-1 at each build, so the fix needs no new Sleeper call.
- Sleeper closes leg N-1 before the Tuesday build. The saved `transactions_prev.json` of weeks 7 and 8 equal the live legs, row for row.
- `bid_history` then reads complete files with no change. The weekly `publish` may stage `clients/<slug>/data/<season>/`, so the rewritten file ships.
- The live path, `save_raw_to_history` (`live.py`, line 290), writes leg N-1 on the Tuesday before the run. The next weekly build then overwrites it with the full leg, so this fix covers it too.

A smaller fix is to make `bid_history` read `_fresh_transactions`. It fixes the board, but the stored files stay short, and each new reader must know the swap. It does not meet "the stored history is complete".

The last leg stays short until the next build. The board of week N reads leg N from the raw file of the build, before its run. That is correct: the run has not happened yet.

The backfill:

- CPC week 6: copy `week-07/raw/transactions_prev.json` (83 rows). CPC week 7: copy `week-08/raw/transactions_prev.json` (59 rows). Both equal the live API.
- CPC week 8: fetch leg 8 now (42 rows). Or let the week 9 build write it through the fix.
- NorCal: no backfill. Weeks 1 to 8 are complete.
- A backfill changes no published page by itself. The trades, the adds, and weeks 6 and 7 of `managers.json` already read the fresh copy.
- A rebuild after the backfill changes `managers.json` week 8 (8 rosters) and the week 8 `waiver.json` (21 bids, 5 `last_like` entries). The week 8 run is over, so a rebuild of that board has no use. The week 9 board is the first to gain.
