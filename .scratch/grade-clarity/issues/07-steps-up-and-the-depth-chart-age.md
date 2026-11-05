# 07: Steps up, and the depth chart age

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests AT-15, AT-16, and AT-30.

**App:** pipeline

**What to build:** A Week line names a player who steps up: the player directly ahead of him on his NFL team's depth chart, at his position, is out for that week. It names no step-up when the newest depth chart is more than 48 hours old. A cached grade changes when the depth chart or a status that a Week line reads changes.

**Blocked by:** 06.

**Status:** ready-for-agent

- [ ] The rule reads the full Sleeper players file, so a player ahead on no roster counts.
- [ ] The depth chart reader gives back the newest `dt` with the charts.
- [ ] With the grade time more than 48 hours after `dt`, no Week line names a step-up.
- [ ] The result cache key holds `dt` and each status that a Week line reads. A change of either gives a new key.
- [ ] `make check-fast` passes at the root.
