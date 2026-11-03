# 01: The calendar trade window

**What to build:** The trades on a week's page are the ones made in the calendar span from the Tuesday cutoff that opens the week to the Tuesday cutoff that opens the next. Build time plays no part. A week 6 build from the saved data lists five trades, the Tuesday 11:56 trade is out, and a week 7 window holds it.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] The window of week N is after the Tuesday cutoff of week N and up to and including the Tuesday cutoff of week N+1. The cutoff function that exists gives both bounds.
- [x] The helper that reads the previous build's fetch time goes, with its tests and its import in the pipeline.
- [x] The pipeline's window helper no longer takes or uses a build fetch time as the end bound. The fetch time stays in the build record.
- [x] Both Sleeper transaction legs, N and N-1, are still fetched and merged, and the fresh-copy and history-copy fallback logic stays as it is.
- [x] The trades module docstring states the calendar rule and no longer says a trade belongs to the week whose build first saw it.
- [x] Tests on the week 6 fixture: the window holds the five trades made before 2026-10-20 08:00 Eastern, drops the trade made at 11:56, and a week 7 window holds that trade. The tests that assert a fetch-time bound change to the cutoff bound.
- [x] A build from disk of week 6 with the fixture writes a bundle with five trades.
- [x] The glossary terms for the trade window and the Tuesday cutoff already match. Do not change them.
- [x] `uv run pytest -q` passes with no failed test.
