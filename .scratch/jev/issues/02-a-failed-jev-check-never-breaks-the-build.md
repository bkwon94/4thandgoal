# 02: A failed Jev check never breaks the build, and the log shows the Jev line

Spec: `.scratch/jev/PRD.md`. Acceptance tests AT-3 and AT-7.

**App:** pipeline

**What to build:** A Jev check that fails, for any reason, never stops the weekly build and never counts as a pass. A missing `TYPESAFE_API_KEY`, an HTTP error, a timeout, or a bad response logs one warning per checked attempt and records the error text in the `jev` of that attempt in `verify.json`. The blurb, `passed`, and the page stay as they would be with no Jev check. The build log also prints one Jev line per build, with the count of Jev checks, the count of errors, and the token use.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] A `run_build` test with `FakeJev` raising the adapter's error shows the error in `verify.json`, one warning per checked attempt, and the same blurbs and `passed` as a run with no error.
- [ ] The real rebuild of 2026 week 8 for cpc with `TYPESAFE_API_KEY` unset exits 0 and writes `page.json`, with an error in every checked `jev`.
- [ ] The real rebuild of 2026 week 8 for cpc with the key prints one Jev line, and its count of checks equals the attempts with a `jev` in `verify.json`.
