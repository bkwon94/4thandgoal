# 06: A writer port with one fake, and no patch of a port

Spec: `.scratch/rules-as-checks/PRD.md`, part 6 and "A fake is not a mock mode". One 0004.

**What to build:** A `Writer` protocol for the Claude call, one implementation, and one in-memory fake. The 20
tests that `monkeypatch` the Claude call or Sleeper move to the fakes or to an injected HTTP transport.
`tests/test_rule_ports.py` then fails on any `monkeypatch.setattr` of a provider or writer target.

**Blocked by:** 04 (the report shape and its helper).

**Status:** ready-for-agent

- [x] `src/cornerstone/claude_port.py`, layer `provider` in `LAYER_OF`, beside `claude_errors`: `class Writer(Protocol)` with one method `parse`. It has the signature of today's `parse_call`, which every Claude call goes through.
- [x] `writer.py`: `ClaudeWriter(client: anthropic.Anthropic | None = None)` implements `Writer`. `parse` holds the body of `parse_call`. It makes the client on its first call, never at import. `_get_client` and the module `_client` go.
- [x] Choice: `parse_call`, `claude_call`, and `analyzer_call` stay as thin functions over one module `ClaudeWriter()`. Their nine import sites do not change.
- [ ] `cli.main(argv, *, writer: Writer | None = None, provider: Provider = SLEEPER, fetch_state=fetch_state)`. The CLI builds its three calls from `writer`.
- [ ] Choice: `fetch_state` stays a one-fetch callable, not a sixth `Provider` method, as ticket 09 of `modular` kept for live and history.
- [ ] `tests/fakes.py` gains `FakeWriter`, annotated as `Writer`, beside `FixtureProvider`. It takes a list of answers, keeps each call in `calls`, and gives the next answer. With no answer left, it raises `WriterError`, as a failed Claude call does. `tests/conftest.py` gains a `fake_writer` fixture.
- [ ] Choice: the fake class lives in `tests/fakes.py`, not in `conftest.py`, because the provider fake is there. One file holds every fake.
- [ ] The Sleeper functions and `SleeperProvider` take `transport: httpx.BaseTransport | None = None` and pass it to `httpx.Client`.
- [ ] Move each patch. Claude, 9: `tests/test_cli.py:32`, `:58`, `:75`, `:537`, `:559`, `tests/test_pipeline.py:1050`, `tests/test_writer.py:273`, `tests/test_chart.py:392`, `tests/test_waiver_research.py:133`.
- [ ] Sleeper, 11: `tests/test_sleeper.py:51`, `:85`, `:146`, `:179`, `:204`, `:206`, `:209`, `tests/test_waiver_trending.py:40`, `tests/test_cli.py:55`, `:160`, `:177`.
- [ ] A test that says "must not call Claude" passes a `FakeWriter` and asserts `calls == []`.
- [ ] The three `_get_client` tests check the request shape of `ClaudeWriter`. They pass their stub client to `ClaudeWriter(client=...)`.
- [ ] The Sleeper adapter tests pass `httpx.MockTransport(handler)`, as `tests/test_sleeper.py:63` does today. It is httpx's in-memory transport at the HTTP edge, not a patch.
- [ ] Rule id `ports/monkeypatch`. The test reads each `monkeypatch.setattr` call in `tests/` with `ast`. It fails when the first argument is a string under `cornerstone.writer`, `cornerstone.claude_port`, `cornerstone.provider`, or `cornerstone.sleeper`. It fails when the first argument is a name imported from one of those modules.
- [ ] It also fails when the attribute is `claude_call`, `analyzer_call`, `parse_call`, `_get_client`, `fetch_state`, or a `Provider` method name.
- [ ] Out of scope: the patches of `fetch_nflverse`, `live_snapshot`, `run_build`, and the other build steps.
- [ ] A test runs the rule on a temporary test file with `monkeypatch.setattr(cli, "claude_call", f)`, and finds one offense.
- [ ] `docs/adr/0010-a-port-has-one-fake.md`: each port has one fake in `tests/fakes.py`. No test patches a port. A fake is a test double that only tests import. A mock mode is a runtime switch that serves fake data, and it stays banned.
- [ ] `src/cornerstone/README.md`, if ticket 05 merged, lists `Writer` under Ports.
- [ ] Add the new module and the test to the `pyright` include list. `make check` passes. The four golden tests pass with no change.
