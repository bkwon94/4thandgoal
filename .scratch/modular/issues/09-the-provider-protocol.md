# 09: The `Provider` protocol

**What to build:** A provider package with a base module that declares a protocol of five methods: fetch the week, fetch live, fetch a past leg, fetch the players, fetch the projections. The return types are the raw models from ticket 08. The Sleeper module implements the protocol. The no-network fetcher in the test conftest satisfies it, which the type check proves.

**Blocked by:** 02, 08

**Status:** done

- [ ] The protocol has five methods, each with typed inputs and a raw model return type.
- [x] The orchestrator calls the provider through the protocol type, with the config for the league id. The live module and the history module keep one-fetch callables with Sleeper defaults, so a test fakes one fetch and not five; a comment in the live module says so.
- [x] The fixture provider in `tests/fakes.py` is annotated as the protocol, and `pyright` accepts it. A broken parameter type fails the check.
- [ ] The four golden tests pass with no golden change.
- [ ] The module this ticket makes is in the `pyright` include list, and `make typecheck` passes.

## Comments

- 2026-10-31: merged into `modular` from branch `modular-09-provider`, commits 76ff01e, 0d62081, and 2aeeba1. 1,505 tests collected. The protocol takes the league id, not the config, because the provider is the lowest layer. The raw models sit in `provider/raw.py`, so the protocol does not import the adapter. `cornerstone.sleeper` stays as a re-export until ticket 16. Two reviewers passed it after one fix pass.
