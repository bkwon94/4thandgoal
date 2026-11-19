# 02: The flaky-test rule

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-30 and AT-31.

**App:** both

**What to build:** `AGENTS.md` says to fix the cause of a flaky test or to delete it with the reason in the commit, and that a second run is never the fix. A rule test of the root scripts fails on each retry setting.

**Blocked by:** none

**Status:** done

- [x] `AGENTS.md` holds the rule in the words of AT-31.
- [x] The rule test fails on a `retries` value above 0 in a Playwright config, and names the file.
- [x] The rule test fails on `pytest-rerunfailures` in a lock file or a config, and on a `retry` in a Vitest config.
- [x] The rule test passes on the configs of `main`.

## Comments

Closes with the squash merge of the spec PR: `trusted-green-02` (`756a9bdc`) merged into `trusted-green` as `46cf9cc9` on 2026-11-18.
`scripts/test_retry_rule.py` has 9 tests, and AT-30 and AT-31 have PASS.
The builder did not count the files it read; the ticket commit changed 3 files: AGENTS.md, scripts/retry_rule.py, scripts/test_retry_rule.py.
