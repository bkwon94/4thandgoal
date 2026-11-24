# 10: The playoff weeks, the file size, and the release check

Spec: `.scratch/playoff-paths/PRD.md`. Acceptance tests AT-19, AT-23, AT-51, and AT-55.

**App:** both

**What to build:** In the playoff weeks the page shows the bracket view of the season sim, with no Goal switch and no board. `sim.json` stays at 50 KB gzip or less. The site holds no push notification. After the merge, 10 real What-if calls on Fly at `cpc` week 11 stay at a median of 2.5 s or less; if not, the fallbacks of decision 03 apply.

**Blocked by:** 05, 06, 07, 08, 09

**Status:** ready-for-agent

- [ ] The playoff fixture shows the bracket view with no Goal switch and no board.
- [ ] `sim.json` of `cpc` weeks 10 and 11 is 50 KB gzip or less.
- [ ] A search finds no service worker, `Notification`, or `PushManager`.
- [ ] After the merge, the median of 10 What-if calls on Fly is 2.5 s or less.
- [ ] `make check-fast` passes.
