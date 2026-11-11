# 38: The rate limit counts questions, not the reads of the page

Spec: `.scratch/front-door/PRD.md`. Source: H24 of `.scratch/front-door/HANDS-ON.md`.

**App:** API

**What to build:** the API allows 10 requests per minute per address over every route (`RATE_LIMIT_PER_MINUTE`, `_guard` in `app.py`). One question now makes 3 to 4 requests, so a second question hits the limit. The cheap read routes (`/suggestions`, `/personal/current`) stop counting toward the limit; they still check the passphrase. The default limit goes to 30 per minute. The cost caps (25 Answers per team per day, $25 per league per month) do not change.

**Blocked by:** none

**Status:** in-review

- [x] `/suggestions` and `/personal/current` check the passphrase and do not count toward the limit.
- [x] `RATE_LIMIT_PER_MINUTE` is 30.
- [x] A test: 3 questions in a row, each with its reads, get no 429 at the default limit.
- [x] The 31st counted request in a minute still gets 429.
