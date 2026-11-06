# 02: The name and the guard of the rate limit setting

Map: `.scratch/faster-evidence/MAP.md`.

**Kind:** spec

**Blocked by:** none

**Status:** open

## Question

`apps/api/src/cornerstone_api/app.py` hard-codes `RATE_LIMIT_PER_MINUTE = 10`, so each analyzer test waits 61 s. The spec names an env var, such as `CORNERSTONE_RATE_LIMIT_PER_MINUTE`, with the default 10. Fly never sets it, so production keeps 10.

## Decision

None yet.
