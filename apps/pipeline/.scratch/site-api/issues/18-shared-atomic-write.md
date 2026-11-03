# 18: One shared helper for the temp-file write

**What to build:** Four modules hold the same block: write to a temp file in the target dir, then `os.replace`, and unlink the temp file on failure. They are `src/cornerstone/chart.py` `_write_bytes`, `src/cornerstone/nflverse.py` near line 62, `src/cornerstone/sleeper.py` near line 77, and `src/cornerstone_api/ratelimit.py` `GradeLimiter._write`. Move the block into one helper, for example `src/cornerstone/files.py` `write_bytes_atomic`, and call it from all four.

**Why:** The review of ticket 17 found the fourth copy. One helper means one place to fix a write bug.

**Blocked by:** 17 (the fourth copy lands with it).

**Status:** done, branch `atomic-write`

- [x] One helper with the file header comment and the reason for the temp file.
- [x] All four call sites use it. No behavior change.
- [x] `uv run pytest -q` passes with no failed test.
