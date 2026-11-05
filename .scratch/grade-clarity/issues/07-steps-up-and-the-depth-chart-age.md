# 07: Steps up, and the depth chart age

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests AT-15, AT-16, and AT-30.

**App:** pipeline

**What to build:** A Week line names a player who steps up: the player directly ahead of him on his NFL team's depth chart, at his position, is out for that week. It names no step-up when the newest depth chart is more than 48 hours old. A cached grade changes when the depth chart or a status that a Week line reads changes.

**Blocked by:** 06.

**Status:** done

- [x] The rule reads the full Sleeper players file, so a player ahead on no roster counts.
- [x] The depth chart reader gives back the newest `dt` with the charts.
- [x] With the grade time more than 48 hours after `dt`, no Week line names a step-up.
- [x] The result cache key holds `dt` and each status that a Week line reads. A change of either gives a new key.
- [x] `make check-fast` passes at the root.

## Comments

- The snapshot holds `ahead_on_chart`: the player directly ahead of each player on his NFL team's depth chart at his position, built from the full Sleeper players file. The id map and the `gsis_id` of the Sleeper file join the gsis_ids to Sleeper ids. A player whose Sleeper team or position differs from the chart has no entry. The snapshot also holds `depth_chart_dt`.
- `read_depth_charts` gives back `DepthCharts(charts, dt)`. The slow sources and the snapshot carry `dt` as `depth_chart_dt`.
- The tunable is `STEP_UP_CHART_HOURS = 48` in `analyzer/tunables.py`. A chart exactly 48 hours old still names a step-up.
- The cache key holds the chart `dt`, a flag for a fresh chart, and the status of each player on the rosters in the trade and of the player ahead of each of them, with his return week. A status the Week line never counts, such as Questionable, reads as none, so it keeps the hit.
- `DOCUMENT_VERSION` goes to 17.
- The tests read a new fixture `apps/pipeline/tests/fixtures/nflverse-2026-11-03/`: the newest real depth chart of 2026-11-03T07:02:07Z, cut to QB, RB, WR, and TE, and the id map rows of its players.
- Real data, week 9: roster 8 gives Carnell Tate to roster 2 for Wan'Dale Robinson. The week 9 line of roster 8 reads "Week 9: WRs in the top 36 who play stay at 1. Robinson has a bye. Lemon and Godwin step up." Lemon is behind Dontayvion Wicks, who is Out and on no roster. Godwin is behind Emeka Egbuka, who is Out. Robinson is behind Tate, but TEN has its bye in week 9.
- For Brian, AT-15: the SF WR directly behind Mike Evans is Deebo Samuel Sr. of roster 10. Samuel is Out himself, so the code names no step-up for him. The SF WR behind Samuel is Jordan Watkins, who steps up but is on no roster. So AT-15 as written gives no step-up. The evidence stage can use the Tate and Robinson trade above.
- For Brian: a player who is out himself, or whose team has a bye that week, does not step up. The PRD does not say this.
- For Brian: a grade with no grade time, such as a saved week, names no step-up, because the age of the chart is not known. The live path and the API always give the time.
- For Brian: an API test of ticket 06 on the Tuesday flag now holds no chart time, because the age of the chart also changes the key.
- The merge: `3ed6622` into `grade-clarity` on 2026-11-05. `make check BASE=main` passed.
