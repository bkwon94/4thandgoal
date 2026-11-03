# 17: Harsher limits on the analyze route

**What to build:** The analyze route allows 5 grades per minute and 20 per day per client address. The teams and refresh routes keep the general limit of 10 requests per minute. A cached repeat of the same trade does not count, because it costs no Claude call. The daily count lives in a file on the Fly volume, so a restart or a deploy keeps it. The day is a calendar day in Eastern time.

**Why:** The commissioner wants a hard cap on the Claude bill from one browser.

**Blocked by:** None (can start immediately).

**Status:** in-progress, branch `grade-limits`

- [x] `GRADES_PER_MINUTE = 5` and `GRADES_PER_DAY = 20` in `src/cornerstone/tunables.py`, with the reason.
- [x] The analyze route counts a grade after the result cache misses and before the Claude call.
- [x] The 429 body names the limit: the minute or the day. `Retry-After` is the seconds to the end of the window.
- [x] The daily counts persist in a JSON file under the result cache dir. A bad or missing file starts at zero.
- [x] Tests: the sixth grade in a minute is 429; the twenty-first in a day is 429 across a restart; a cached repeat does not count; another address is unaffected.
- [x] The runbook names both limits and the file.
- [ ] Site follow-up, separate: show "Try again in N hours" when `Retry-After` is over an hour.
- [x] `uv run pytest -q` passes with no failed test.
- [ ] Deploy needs Brian's `fly deploy`.
