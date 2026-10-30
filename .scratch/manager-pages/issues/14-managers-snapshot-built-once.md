# 14: The managers snapshot is built once

**What to build:** `_write_managers` and `_managers_snapshot` both build the raw dir, and both callers pass `snapshot=_managers_snapshot(...)`. So `load_raw(raw_dir)` runs twice. Let `_write_managers` build the snapshot. Also, `(snapshot, projections_ahead, history, chart)` travels together through five functions, and `dict[int, dict[str, float]]` stands in for the projections ahead in six signatures. Consider one type for the clump. Pipeline repo.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `load_raw(raw_dir)` runs once per managers build.
- [ ] `_write_managers` builds the snapshot, and no caller passes one.
- [ ] Brian decides whether one type holds the clump and the projections ahead. If yes, the signatures use it.
- [ ] Every existing test passes. The managers file does not change. `ruff` is clean.
