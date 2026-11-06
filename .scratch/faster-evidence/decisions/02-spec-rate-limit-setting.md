# 02: The name and the guard of the rate limit setting

Map: `.scratch/faster-evidence/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** done

## Question

`apps/api/src/cornerstone_api/app.py` hard-codes `RATE_LIMIT_PER_MINUTE = 10`, so each analyzer test waits 61 s. The spec names an env var, such as `CORNERSTONE_RATE_LIMIT_PER_MINUTE`, with the default 10. Fly never sets it, so production keeps 10.

## Decision

The spec records it, approved by Brian on 2026-11-05. The API reads `CORNERSTONE_RATE_LIMIT_PER_MINUTE`, with the default 10. Fly never sets it. A make target `api-evidence` runs the local API with a limit of 600. See `PRD.md`, Implementation Decisions.
