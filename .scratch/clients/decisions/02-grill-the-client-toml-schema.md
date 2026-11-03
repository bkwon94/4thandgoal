# 02: The sections and values of `client.toml`

Map: `.scratch/clients/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** open

## Question

What does `client.toml` hold? It replaces the League config (ADR 0022). The spec needs its sections: the league, the provider per season, the package list, the values of each package, the menu, the brand, and the copy. It also needs the rule for each value that the check reads, and the error when a value is missing. Decide which values sit in `client.toml` and which get their own file, as in One ADR-0009.

Decision 01 note: Decision 01 sets the package list: `league`, `facts`, and `design` are in every client, and `week`, `rankings`, `managers`, `waiver`, and `analyzer` are the choice. Each package owns a `tunables` module, and a client sets only the values that its README names. A client may also choose its AI service, as one value behind the Writer port. `config.py` moves into `league`, so decide what is left of it.

## Decision

None yet.
