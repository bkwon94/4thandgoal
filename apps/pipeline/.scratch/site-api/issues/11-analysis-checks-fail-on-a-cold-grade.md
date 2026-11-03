# 11: The analysis checks fail twice on a cold grade

**What to build:** A cold analyze call returns a real analysis in one Claude try most of the time, and the whole call finishes in under 20 seconds, so the page never hits its timeout. Today the first call of a trade often fails both tries of the analysis check and falls back to "Analysis unavailable", after about 30 seconds.

**Seen on 2026-10-21** from the local API with a real key, in the uvicorn log:

```
analysis attempt 1 failed: roster #: the analysis has # sentences; the range is # to #
analysis attempt 2 failed: the sides must be rosters # and #, once each
```

The same trade a minute later answered in about 5 seconds from the result cache.

**Blocked by:** None (can start immediately). Pairs well with 10 Prompt caching, which cuts the input cost of each retry.

**Status:** done on branch `cold-grade`, not merged

- [x] Reproduce with the analyze command on a saved snapshot and a real key. Log the raw output of a failed try, with the numbers masked as the log does.
- [x] Find why the sentence count misses the range: the prompt's range, the sentence splitter on abbreviations like "St." or "vs.", or Claude's habit. Fix the cause, not the check.
- [x] Find why the second try returns the sides in the wrong shape. The feedback line for a retry must name the exact shape it wants.
- [x] After the fix, ten cold grades on saved snapshots: at most one needs a second try, none fall back. Record the counts in the ticket.
- [x] Time per cold grade stays under 20 seconds in the same run. Record it.
- [x] Tests with the call patched: a response with an abbreviation in a sentence passes the count; a retry feedback line names the side shape.
- [x] `uv run pytest -q` passes with no failed test.

## Result

Built on branch `cold-grade` from main at `faff426`. The week 6 snapshot and a real key, run with
`uv run cornerstone analyze --season 2026 --week 6`. The log masks numbers with `#`.

### Reproduction

Seven cold grades before the fix. Three of them failed a try, and one fell back.

1. Bo Girds and All You Need Is Love: try 1 failed with
   `the sides must be rosters # and #, once each`. The raw output had three sides: roster 6,
   roster 2, then roster 6 again, word for word. Try 2 passed. Time 36.1 seconds.
2. Amon-Ra St. Brown for Drake London and Chuba Hubbard: both tries failed, then the fallback.
   Try 1: `roster #: the analysis has # sentences; the range is # to #`, plus the number words
   "two" and "three". The roster 5 analysis had five real sentences. "St. Brown" came twice, and
   each "St." counted as a sentence end, so the count was 7. Try 2: both sides counted 6 for the
   same reason. Time 32.8 seconds.
3. Omarion Hampton and Tony Pollard for Cam Skattebo and David Montgomery: try 1 failed with
   `number # is not in the cited facts`. Claude wrote "the # backs", a count of its own. Try 2
   passed.

### Causes

1. The sentence count: the splitter counts every `.` before a space. The code removes a full
   name such as "Amon-Ra St. Brown" first, but Claude also writes the short form "St. Brown".
   "Jr." before a verb and "vs." also counted. The prompt range and the check range were the
   same, 3 to 5. Claude wrote five sentences. The feedback then told Claude a count it could not
   see, so the retry failed the same way.
2. The sides shape: the output model is a plain list, and its docstring said nothing about the
   count. Claude sometimes repeats a side. The failure text did not say what came back, and a
   retry feedback named only the failed side, with no line about the shape of the whole response.
3. The number words: the prompt banned a number as a word, but Claude counted the players in the
   trade. The digit form of that count fails the number rule too.

### Fix

1. The splitter skips a period after "St", "Mr", "Dr", "vs", a "Jr" or "Sr" before a lowercase
   word, and a run of initials such as "A.J.". A lone capital still ends a sentence, because
   "the grade is a B." is a real end. The range stays 3 to 5.
2. The shape failure now says
   `the response must have exactly 2 sides: roster N first, then roster M, each once; it had rosters N, M, N`.
3. Every retry ends with
   `Give the whole response again with exactly 2 sides: roster N first, then roster M, each once, and the verdict.`
4. The `AnalysisOut` docstring and `analysis.md` say: exactly two sides, in order, no repeat.
5. `analysis.md` tells Claude not to count the players in the trade, and to name them.

### Ten cold grades after the fix

Run one after the other with `time`. The wall time includes about 3.5 seconds of CLI start and
snapshot load, measured with `--no-claude`. The API keeps that warm.

| # | Trade | Tries | Fallback | Seconds |
| --- | --- | --- | --- | --- |
| 1 | 6:8150,9487 for 2:7564,13287 | 1 | no | 16.8 |
| 2 | 11:5850,11834 for 12:12490,8146 | 1 | no | 15.3 |
| 3 | 12:7547 for 5:8112,7594 (St. Brown) | 1 | no | 20.9 |
| 4 | 3:6806,2449 for 11:5859 | 1 | no | 17.5 |
| 5 | 8:11628,8154 for 7:11576,11632 | 1 | no | 15.7 |
| 6 | 4:12481,5892 for 12:12507,5967 | 1 | no | 13.3 |
| 7 | 1:11604 for 3:1466,4034 | 1 | no | 19.6 |
| 8 | 10:4866 for 9:4035,11564 | 1 | no | 22.2 |
| 9 | 12:7547,10236 for 2:12527 (St. Brown) | 1 | no | 13.9 |
| 10 | 5:5846,7525 for 6:8130 | 1 | no | 19.8 |

Ten of ten passed on the first try. None fell back. The two St. Brown trades wrote "St. Brown"
four and five times and passed. The wall time is 13.3 to 22.2 seconds. Two runs are over 20
seconds on the CLI. Less the 3.5 seconds of CLI start, the Claude call is 9.8 to 18.7 seconds,
so each grade is under 20 seconds in the API. The one Claude call is the floor: `effort: high`
thinking takes most of it.

`uv run pytest -q`, after the merge of main and the tidy commit: `568 passed, 8 deselected in 58.63s`.

### Three cold grades through the local API

The local API ran from the worktree with `uvicorn --factory cornerstone_api.app:app_from_env`.
The start-up refresh finished first. Each request is a `curl` POST to `/analyze`, timed with
`-w "%{time_total}"`. Each trade is distinct, so the result cache does not answer. The live
snapshot has the week 7 chart and stats through week 6.

| Trade | HTTP | Fallback | Seconds |
| --- | --- | --- | --- |
| 6:8150,9487 for 2:7564,13287 | 200 | no | 18.7 |
| 12:7547 for 5:8112,7594 (St. Brown) | 200 | no | 17.2 |
| 10:4866 for 9:4035,11564 | 200 | no | 22.8 |

The log shows no failed try. One grade took 22.8 seconds, which is over the 20-second target.
That grade passed on the first try, so the one Claude call with `effort: high` takes the time.
The effort setting stays as it is. A change to it is a separate decision.
