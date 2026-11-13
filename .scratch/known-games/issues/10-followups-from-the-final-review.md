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

**Status:** wontfix

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12. Brian dropped it, because it fixes no real bug and changes nothing that a manager sees.
Proof: No commit after 5b935d74 touches the three items, and `finder_search.py` still calls `season_rank` through `stats_through`, which includes the known games (item 3). Items 1 and 2 may be partly covered by the WOPR rows in the cache key and the stale `stats` flag in `snapshot.py`.
Read 1 file: .scratch/todoist-queue/audit.md.
