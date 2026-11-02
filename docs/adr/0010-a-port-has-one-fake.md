# A port has one fake, and no test patches a port

A port is the edge to an outside system. This repo has two ports. `Provider` in
`src/cornerstone/provider/base.py` fetches the league data. `Writer` in `src/cornerstone/claude_port.py`
makes the one Claude call. `SleeperProvider` and `ClaudeWriter` implement them.

Each port has one fake in `tests/fakes.py`: `FixtureProvider` and `FakeWriter`. Each fake is annotated as
its port, so `pyright` proves that the fake has the methods of the port. A test passes the fake to the
code. No test patches a port. One 0004 gives the reason. A patch spreads one idea of the port across
many test files, so a change to the port edits each of them. The fake holds that idea in one file.

## A fake is not a mock mode

A fake is a test double that only tests import. A mock mode is a runtime switch that serves fake data.
The mock mode stays banned. No module under `src/` imports `tests/fakes.py`, and no flag, setting, or
environment variable makes a run use a fake.

## The seams

- `cli.main` takes a `writer`, a `provider`, and a `fetch_state`. A writer of None is the one
  `ClaudeWriter` of the process, `WRITER` in `writer.py`.
- `parse_call`, `claude_call`, and `analyzer_call` stay as thin functions over `WRITER`. Each takes an
  optional writer, so a caller can pass its own.
- `ClaudeWriter` takes an optional client and makes its client on the first call, never at import. A
  test of the request shape passes a stub client.
- Each Sleeper fetch and `SleeperProvider` take an optional `httpx` transport. A test of the adapter
  passes an `httpx.MockTransport`. That is the in-memory transport of `httpx` at the HTTP edge, not a
  patch of a port.
- `fetch_state` stays a one-fetch callable, not a sixth `Provider` method. The live module and the
  history module keep one-fetch callables for the same reason: a test fakes one fetch, not five.

## The rule

`tests/test_rule_ports.py` holds the rule, with the id `ports/monkeypatch`. It reads each
`monkeypatch.setattr` call in `tests/` with `ast`. It fails when the target is under
`cornerstone.writer`, `cornerstone.claude_port`, `cornerstone.provider`, or `cornerstone.sleeper`. It
fails when the target is a name imported from one of those modules. It also fails when the attribute is
a Claude call, `_get_client`, `fetch_state`, or a `Provider` method. The test reads the method names
from the protocol source, so a new fetch joins the rule by itself.

The patches of the nflverse fetch, of the live snapshot, and of the build steps are out of the rule.
They are not ports.
