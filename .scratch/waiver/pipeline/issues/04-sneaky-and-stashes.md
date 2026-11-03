# 04: Sneaky and stashes

Spec: `.scratch/waiver/pipeline/PRD.md`.

**What to build:** The file gains two buckets. Sneaky: free agents whose usage trend score is in the
top quarter and whose projection score is in the bottom half, or who sit one depth chart slot below
an injured player. Stashes: free agents out or on IR with a return week inside the season and a rest
of season projection in the top half of their position, plus the handcuff rule for a player one slot
below a starter. Each player in these buckets carries a story fact from the injury file and the depth
chart, "Pittman is out, and Bernard is next on the depth chart". Every bucket entry says which rule
put him there.

The return week comes from the hand-kept returns file first and the injury file second. A player in
best adds is not sneaky.

**Blocked by:** 02 Usage and environment.

**Status:** done

- [x] A player with a rising snap share and a flat projection lands in sneaky and not in best adds.
- [x] A player one slot below an injured starter lands in sneaky with the story fact naming the starter.
- [x] A player out with a return week and a top-half rest of season projection lands in stashes.
- [x] A handcuff one slot below a healthy starter lands in stashes when the rule holds.
- [x] A player out with no return week does not land in stashes.
- [x] Each entry carries its bucket reason, and the story fact has no digit that is not in its numbers.
- [x] Glossary gains **Sneaky add**, **Stash**, and **Story fact**.

## Comments

2026-10-23, decisions the ticket left open:
- The injury status is the Sleeper `injury_status`, as the price reads it. The out statuses are `OUT_STATUSES`.
- Sleeper gives an IR player the status Inactive. An active player with that status and an out injury status joins the pool for stashes only. Every other bucket skips a player who is out.
- The injury report has no return field. Its return week is the first week after N with a status that does not keep him out. It gives one only once a later report is out.
- The build reads the slow sources with week N + 1, as the trade analyzer does. The depth chart is the latest one in the cache.
- `behind_injury` wins over `usage_rise`, and `return` wins over `handcuff`, when both rules hold.
- The handcuff rule is RB only, as the glossary defines **Handcuff**. The starter's rest of season projection ranks among every RB with a team, rostered too.
- A stash needs a rest of season projection above 0, because a tie at 0 ranks every player at the top.
- Every ranked player carries a reason: `board_score`, `trending`, `usage_rise`, `behind_injury`, `return`, or `handcuff`. Every pool player carries his bye, his injury status, and his return week.
- The story fact sits on the sneaky and stash entries only.
- The drops bucket compares a drop candidate against the healthy pool only, because a player who is out cannot replace him this week.
- The return window shares `back_inside` with the trade analyzer. The handcuff test does not share code with it: the analyzer asks for second or lower with the starter on a roster, and the board asks for one slot below a healthy top-half starter.

2026-10-23, the real week 6 check: before the fix, eight healthy backups landed in stashes as handcuffs, and two out players landed in sneaky. Every rest of season projection was 0, because the saved raw predates the lifted filter of the projections ahead fetch. After the fix, stashes is empty and sneaky holds eight healthy players behind an out player.
