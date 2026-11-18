# 02: The flaky-test rule

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-30 and AT-31.

**App:** both

**What to build:** `AGENTS.md` says to fix the cause of a flaky test or to delete it with the reason in the commit, and that a second run is never the fix. A rule test of the root scripts fails on each retry setting.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] `AGENTS.md` holds the rule in the words of AT-31.
- [ ] The rule test fails on a `retries` value above 0 in a Playwright config, and names the file.
- [ ] The rule test fails on `pytest-rerunfailures` in a lock file or a config, and on a `retry` in a Vitest config.
- [ ] The rule test passes on the configs of `main`.
