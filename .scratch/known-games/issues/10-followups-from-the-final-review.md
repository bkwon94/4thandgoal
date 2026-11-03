# 10: Follow-ups from the final review

Found in the final whole-branch review on 2026-10-26. None blocks the push.

**What to record:** Three small gaps that the branch leaves open.

1. A teammate's targets during a game move a rostered player's target share, but the cache key hashes only the
   rostered players' lines. The stale period ends when the game ends, because the in-progress set changes.
   Fix later: hash the team target totals of the rostered players' NFL teams.
2. On the Tuesday roll, a failed stats fetch gives `None`, and the snapshot parses week N-1 from an empty list
   with no stale flag, which also replaces a good saved copy in memory. Older than this branch.
   Fix later: on the Tuesday roll, a `None` stats fetch keeps the saved week N-1 and names stats stale.
3. `season_rank` in the trade facts ranks by season totals through the known games, so on a Sunday it favors
   players who already played. Fix later: rank through the completed week, or label the rank.

**Blocked by:** None.

**Status:** needs-triage
