# 12: A cold machine pays the first downloads on the first request

**What to build:** The first `/teams` or `/analyze` request after the Fly machine starts answers in a few seconds, not after the full set of source downloads. Today a cold machine with no cron run that day pays every download on the first request.

**Blocked by:** None (can start immediately).

**Status:** done, by ticket 19

- [ ] Measure a cold `/teams` and a cold `/analyze` on Fly after a machine stop, and record the seconds.
- [ ] Warm the slow sources on machine start, in the background, so the first request finds them on the volume.
- [ ] `/teams` never waits on the chart or the schedule downloads it does not use.
- [ ] After the change, a cold `/teams` answers in under 5 seconds. Record it.
- [ ] Tests cover the start-up warm with the sources patched.
- [ ] The runbook names the start-up warm.
- [ ] `uv run pytest -q` passes with no failed test.
