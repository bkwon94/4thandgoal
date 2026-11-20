# 15: CI runs the unit suite in shards and only the reachable tests on a PR

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-29, AT-30, AT-31, and AT-32.

**App:** root

**What to build:** CI runs `bun test` in a matrix of shards. The time of the full suite with each shard count sets the count. On a PR, CI runs only the tests that the diff can reach. A change to a config file, the lock file, or the test preload runs the full suite. A push runs the full suite.

**Blocked by:** 13

**Status:** ready-for-agent

- [ ] The ticket records the time of the full suite with each shard count it tried, and the chosen count.
- [ ] A PR that changes one file of the rankings package runs fewer test files than the full count.
- [ ] A PR that changes only the lock file runs the full suite.
- [ ] A push runs the full suite, and the workflow gives a push to `main` the same full run.
