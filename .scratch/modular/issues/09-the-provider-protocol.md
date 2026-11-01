# 09: The `Provider` protocol

**What to build:** A provider package with a base module that declares a protocol of five methods: fetch the week, fetch live, fetch a past leg, fetch the players, fetch the projections. The return types are the raw models from ticket 08. The Sleeper module implements the protocol. The no-network fetcher in the test conftest satisfies it, which the type check proves.

**Blocked by:** 02, 08

**Status:** ready-for-agent

- [ ] The protocol has five methods, each with typed inputs and a raw model return type.
- [ ] The orchestrator, the live module, and the history module call the provider through the protocol type, with the config for the league id.
- [ ] The fake fetcher in the conftest is annotated as the protocol, and `pyright` accepts it.
- [ ] The four golden tests pass with no golden change.
- [ ] The module this ticket makes is in the `pyright` include list, and `make typecheck` passes.
