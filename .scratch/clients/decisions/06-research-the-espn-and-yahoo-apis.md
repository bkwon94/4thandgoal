# 06: The ESPN API and the Yahoo API

Map: `.scratch/clients/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

Can the provider port take the ESPN API and the Yahoo API later? This spec builds no provider but Sleeper. But the port must not assume a Sleeper shape. Find the auth of each API, such as the cookies of a private ESPN league and the OAuth of Yahoo. Find the data each gives: rosters, matchups, transactions, and the history of past seasons. Name each field of the models that one of them cannot fill.

## Decision

Brian decided on 2026-11-03, from the notes in `06-research-the-espn-and-yahoo-apis.notes.md`.

Yes, the provider port can take the ESPN API and the Yahoo API later. This spec builds the Sleeper provider only.

1. **The Sleeper player ID is the one canonical player ID.** The `league` README states the rule. A later adapter maps its own IDs to it. No code changes.
2. **The cache path moves into the adapter.** `fetch_week`, `fetch_live`, and `fetch_players` drop the `players_cache` argument. The Sleeper adapter takes its cache dir in its constructor. The change rides on the move of `provider/` into `packages/league`, with an empty CPC golden diff.
3. **The split of `Provider` waits for the ESPN spec.** That spec splits it into a league provider and an NFL data source, and Sleeper stays the NFL data source for every league. NorCal is a Sleeper league, so this spec has no second user to test a split.
4. **The `league` README lists each Sleeper shape in the port as a duty of a later adapter.** The notes list 11 shapes. No code changes.

Two risks go to the later spec of each provider. The ESPN API is unofficial, a person must copy its cookies, and the Disney terms forbid automated access. Yahoo needs an approved app, and CI must store the refresh token again each time Yahoo rotates it.
