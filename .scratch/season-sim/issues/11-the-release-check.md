# 11: The release check

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests AT-22, AT-23, and AT-62. Decision 03.

**App:** api, site

**What to build:** The What-if is timed on Fly, and the new parts of the site carry no banned word. The API of the Spec branch deploys to Fly before the merge. Ask Brian before the deploy, because it is a production deploy. Then time 10 What-if calls of `cpc` on a machine idle for 10 minutes, and 10 calls within 1 minute of a deploy. If the calls are slow, stop and give Brian the times.

**Blocked by:** 04, 05, 06, 07, 08, 09, 10.

**Status:** ready-for-agent

- [ ] Brian approves the deploy of the branch API to Fly.
- [ ] The median of 10 calls on an idle machine is 2.5 s or less (AT-22).
- [ ] The 10 calls just after a deploy each answer 200, and their times are on record (AT-23).
- [ ] The text of the sim page, the Sim tile, and the Announcement in the built `cpc` and `norcal` sites has no "rival", "Brian", "Jev", "Advisor", "Finder", or "front door" (AT-62).
