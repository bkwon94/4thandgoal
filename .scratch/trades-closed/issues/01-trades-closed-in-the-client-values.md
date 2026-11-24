# 01: Trades closed in the client values

Spec: `.scratch/trades-closed/PRD.md`. Acceptance tests AT-10, AT-20, AT-23, and AT-24.

**App:** both. The site and the API.

**What to build:** Each app knows when a client has Trades closed. One small pure function in each app takes the Lock and the time: closed at or after the Lock, never closed with no Lock. The site build computes it once at build time and passes it on in the generated client values. The API parses `lock` from the client values. NorCal gets `lock = "2026-12-15T00:00:00-05:00"`. A new value `deadline_week` under `[values.analyzer]`, false by default, turns on the Deadline banner and the Trade Wire. CPC sets it to true. The Deadline banner shows only with `deadline_week` and only before the Lock, so the one closed day after the Lock goes away. The glossary entry of Deadline week names `deadline_week`.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] A unit test in each app shows that a client with no `lock` is never closed, at 2026-11-24 12:00 and 2027-06-01 12:00 Eastern (AT-23).
- [ ] A unit test in each app shows closed at the Lock and open 1 s before it.
- [ ] `clients/norcal/client.toml` holds the NorCal `lock` and no `deadline_week`. `clients/cpc/client.toml` holds `deadline_week = true` (AT-24).
- [ ] A `cpc` build made today shows no Deadline banner on `/`, `/rankings/`, and `/analyze/` (AT-10).
- [ ] A `norcal` build made today shows no Deadline banner (AT-20).
- [ ] The full site and API suites pass, because some tests read the real `client.toml`.
