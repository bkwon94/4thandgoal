# 01: Four golden files and `make golden`

**What to build:** A build over the week 6 fixtures, with the template fallback and the no-network fetcher, writes `facts.json`, `page.json`, `rankings.json`, and `managers.json`. One test per file compares the bytes to a saved golden copy. `make golden` rewrites the four copies. This is the seam every later ticket proves itself against.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Four golden files sit under the test fixtures, built from the week 6 raw files and the week 1 to 5 history.
- [ ] The page golden uses template blurbs. The test makes no Claude call and no network call.
- [ ] One test per file fails on a one-byte difference and names the file.
- [ ] `make golden` rewrites the four files. The Makefile target has a one-line comment that says a golden change must show in review.
- [ ] The full suite passes. The count is 1,455 or more plus the four new tests.
