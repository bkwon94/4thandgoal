# 07: What shape does the Jev port take?

Map: `.scratch/jev/MAP.md`.

**Kind:** spec

**Blocked by:** 01

**Status:** done

## Question

The port sits beside `Writer` in `league/claude_port.py`. Every outside service enters through the league package.
The spec chooses: the `typesafe-sdk` package or plain HTTP, the sync or the async client, and the one fake in `tests/fakes.py`.
All question text, criteria, and thresholds live in one module, so a person can audit and edit them in one place.

## Decision

The spec records it under The port. A `Jev` Protocol in the league package's provider layer, one Noul method, the sync `typesafe-sdk` client with model `jev-latest`, one error type, and `FakeJev` as the one fake. Brian approved the spec on 2026-11-09.
