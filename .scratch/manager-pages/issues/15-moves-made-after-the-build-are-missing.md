# 15: Moves made after the Tuesday build are missing from the manager pages

**What to build:** The week N build runs Tuesday at 08:00 ET and saves the leg N transactions to `data/<season>/week-NN/raw/transactions.json`. Sleeper keeps the leg at N until the next week starts, so every add and drop from Tuesday 08:00 ET to the leg change lands in leg N after the build. The Tuesday night waiver run is in that span. The history copy of week N never sees them, and `roster_moves` reads the history copy, so the Moves chapter of every manager page misses them. Week 6 misses 15 completed adds and drops out of 83. Bo Girds' Texans waiver add of 2026-10-20 08:01 ET is one of them. Trades have a fix already: the week N fetch saves a fresh copy of leg N-1 as `transactions_prev.json`, and `_window_trades` reads it. Let the history read the fresh copy too, then backfill the fresh copies for weeks 1 to 6 from Sleeper and rebuild the managers file. Pipeline repo.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] `load_saved_weeks` reads week N's transactions from `week-(N+1)/raw/transactions_prev.json` when that file exists, and from `week-NN/raw/transactions.json` otherwise. A comment says why.
- [x] `_window_trades` keeps its result on the current fixtures.
- [x] A one-off fetch writes `transactions_prev.json` for weeks 2 to 7 from Sleeper's leg 1 to 6 lists, and the files are committed. Sleeper serves a past leg in full at any time.
- [x] The week 7 managers file is rebuilt and committed. Bo Girds' week 6 adds hold the Houston Texans.
- [x] A test with a fixture pair shows an add in the fresh copy and not in the saved copy lands in the moves.
- [x] The site gets the rebuilt file on `main` and the deploy runs.

## Comments

- 2026-10-29: The history reads the fresh copy of each leg. Legs 1 to 5 are backfilled, and week 7 already held leg 6. Only week 6 had a gap: 15 of 83. Bo Girds' week 6 adds hold HOU.
- 2026-10-29: merged as e658aca and pushed. The site has the rebuilt file in dd29ecb, and the deploy ran.
