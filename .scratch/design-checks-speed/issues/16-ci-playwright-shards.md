# 16: CI runs Playwright in shards

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-29.

**App:** root

**What to build:** CI runs Playwright in a matrix of shards. The serial projects keep one worker. The measured split sets the shard count.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] The ticket records the time of each shard with each count it tried, and the chosen count.
- [ ] The serial Playwright projects run with one worker.
- [ ] Each Playwright shard job exits 0 in 360 s or less.
