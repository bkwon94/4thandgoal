# 16: Importers read the provider package, and the re-export goes

**What to build:** Every importer of the Sleeper module reads `cornerstone.provider.sleeper` or `cornerstone.provider.raw`, and the thin re-export module `cornerstone.sleeper` is deleted. Ticket 09 left the re-export so no importer changed in that ticket.

**Blocked by:** 09

**Status:** done

- [ ] `src/cornerstone/sleeper.py` does not exist. A grep for `cornerstone.sleeper` and `from cornerstone import sleeper` finds nothing in `src/` or `tests/`.
- [ ] The four golden tests pass with no golden change.
- [ ] `make typecheck` passes.

## Comments

- 2026-11-01: merged into `modular` from branch `modular-16-provider-imports`, commit 709e4e3. 1,509 tests collected. 51 files, import lines only plus the deleted re-export. Two reviewers passed it.
