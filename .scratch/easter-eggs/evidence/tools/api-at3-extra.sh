#!/bin/bash
# The extra evidence of AT-3: a twin of T2 on the real clock, then the API test of the window of T2.
source "$(dirname "$0")/lib.sh"
OUT=$EV/AT-3/output.txt
note "An extra real check on the real clock: a twin of T2 for week 12 with a window that holds now, 00:00-02:00 ET."
run "TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z'"
run "curl -s -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":12,\"eggs\":[{\"page\":\"/2026/week-08/\",\"target\":\"number-median\",\"action\":\"tap2\",\"conditions\":{\"clock\":\"00:00-02:00\"}}]}'"
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/check -H '$J' -d '{\"page\":\"/2026/week-08/\",\"target\":\"number-median\",\"action\":\"tap2\",\"conditions\":{}}' | sed -E 's/\"token\":\"[^\"]+\"/\"token\":\"<cut>\"/'"
note "The check inside the window of T2 itself, 11 PM to midnight ET: only a test can set the clock of the API, so the API test that covers it is the evidence."
note "The test sets the clock to 22:59 ET (no match), 23:30 ET (match), 23:30 Los Angeles (no match), and 00:00 ET (no match)."
run "cd /Users/brian.kwon/repos/cpcfantasyfootball/.claude/worktrees/easter-eggs/apps/api && uv run --exact --package cpc-api pytest -q -v 'tests/test_eggs.py::test_a_clock_window_egg_matches_only_inside_the_window_in_the_timezone_of_the_client' 2>&1 | tail -4"
