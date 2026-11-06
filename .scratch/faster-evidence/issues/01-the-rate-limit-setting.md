# 01: The rate limit setting and make api-evidence

Spec: `.scratch/faster-evidence/PRD.md`. Acceptance tests AT-9 and AT-8.

**App:** pipeline

**What to build:** The API reads its rate limit from `CORNERSTONE_RATE_LIMIT_PER_MINUTE`, with the default 10. A new make target `api-evidence` of the API runs the local API with a limit of 600, so an analyzer test of an evidence run does not wait 61 s. Production keeps 10, because Fly never sets the value. The API stays real.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] A test sets the value to a count, and the app allows that count in one minute, then answers 429.
- [ ] A test with the value unset proves the limit of 10.
- [ ] `make -C apps/api api-evidence` starts the API, and 11 requests to `/teams` in one minute all answer 200.
- [ ] `apps/api/fly.toml` does not set `CORNERSTONE_RATE_LIMIT_PER_MINUTE`.
- [ ] `make check-fast` of the API passes.
