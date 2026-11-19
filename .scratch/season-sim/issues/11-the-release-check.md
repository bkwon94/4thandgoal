# 11: The release check

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests AT-22, AT-23, and AT-62. Decision 03.

**App:** api, site

**What to build:** The What-if is timed on Fly, and the new parts of the site carry no banned word. The API of the Spec branch deploys to Fly before the merge. Ask Brian before the deploy, because it is a production deploy. Then time 10 What-if calls of `cpc` on a machine idle for 10 minutes, and 10 calls within 1 minute of a deploy. If the calls are slow, stop and give Brian the times.

**Blocked by:** 04, 05, 06, 07, 08, 09, 10.

**Status:** in-review

- [x] Brian approves the deploy of the branch API to Fly.
- [x] The median of 10 calls on an idle machine is 2.5 s or less (AT-22).
- [x] The 10 calls just after a deploy each answer 200, and their times are on record (AT-23).
- [x] The text of the sim page, the Sim tile, and the Announcement in the built `cpc` and `norcal` sites has no "rival", "Brian", "Jev", "Advisor", "Finder", or "front door" (AT-62).

## Comments
- 2026-11-18: Brian approved the deploy in the session. `fly deploy` from the Spec branch at dbea219f made release v62 at 02:35 to 02:36 UTC on 2026-11-19.
- AT-23: 10 calls from 02:36:00 to 02:36:19 UTC, each 200, median 1.788 s, min 1.691 s, max 1.893 s.
- AT-22: no What-if call from 02:36:19 to 02:46:55 UTC, then 10 calls, each 200, median 1.727 s, min 1.546 s, max 1.898 s. The AT-62 check loaded the built home pages at about 02:39 UTC, which may make small API calls such as the egg board, but no What-if call.
- AT-62: the built `cpc` and `norcal` sites, rendered in WebKit at 390x660 with roster 6 kept, show no banned word on the sim page, the replay, the Sim tile, or the Announcement. The static HTML of the norcal week 10 page holds "Brian Robinson Jr.", an NFL player in the Next week byes, outside the new parts.
