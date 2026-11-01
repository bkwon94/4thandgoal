# 08: Pydantic raw models at the Sleeper call

**What to build:** The raw Sleeper shapes become pydantic models in the Sleeper module: the state, the league, a user, a roster, a matchup, a transaction, a projection row, a stats row. The fetch functions return them, and the parser takes them. The `dict` stops at the HTTP call. Sleeper field names stay in the adapter and the models. The fixture raw files load through the models, which is the contract test.

**Blocked by:** 01

**Status:** done

- [ ] Every raw fixture file loads through its model with no extra field dropped and no error.
- [ ] The parser's signatures take the raw models, not `dict`.
- [ ] The saved raw files on disk keep their shape. A build from an existing raw directory still works.
- [ ] The four golden tests pass with no golden change.

## Comments

- 2026-10-31: merged into `modular` from branch `modular-08-raw-models`, commits b1eded1, c20d994, and the merge 8013e1c. 1,499 tests collected. Every raw model allows extra fields and names only what the code reads. The `players` map stays a dict for size. One byte-level change: the history files the live path writes come out of `model_dump`, so the key order differs from the fetch; the JSON is equal, and a history file is written once and never rewritten. The contract test compares sorted JSON text, so an int-to-float change would fail; none occurs. Two reviewers passed it after one fix pass.
