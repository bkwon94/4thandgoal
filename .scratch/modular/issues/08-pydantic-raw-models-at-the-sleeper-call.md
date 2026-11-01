# 08: Pydantic raw models at the Sleeper call

**What to build:** The raw Sleeper shapes become pydantic models in the Sleeper module: the state, the league, a user, a roster, a matchup, a transaction, a projection row, a stats row. The fetch functions return them, and the parser takes them. The `dict` stops at the HTTP call. Sleeper field names stay in the adapter and the models. The fixture raw files load through the models, which is the contract test.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Every raw fixture file loads through its model with no extra field dropped and no error.
- [ ] The parser's signatures take the raw models, not `dict`.
- [ ] The saved raw files on disk keep their shape. A build from an existing raw directory still works.
- [ ] The four golden tests pass with no golden change.
