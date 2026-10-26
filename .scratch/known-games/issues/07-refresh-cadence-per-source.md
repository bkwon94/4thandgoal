# 07: Refresh cadence per source

Spec: `.scratch/known-games/PRD.md`, "Refresh cadence".

**What to build:** The refresh takes a max age per source. The injuries file and the player weeks file refresh
when older than 6 hours. Every other refreshed source keeps 24 hours. The live path, the refresh route, and the
start-up refresh all pass the per-source ages the same way, so a Monday morning grade sees the Sunday snaps and
the Sunday WOPR. The refresh route's forced refresh, max age zero, still fetches every source.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] An injuries file 7 hours old refreshes on the live path, and the result names it as refreshed.
- [ ] A player weeks file 7 hours old refreshes on the live path.
- [ ] A schedules file 7 hours old does not refresh, and a schedules file 25 hours old does.
- [ ] A failed 6-hour refresh keeps the old file and does not name it stale while the file is under a day old.
- [ ] The refresh route with max age zero fetches every source.
- [ ] Every existing live test passes unchanged.
