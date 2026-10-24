# 04: Sneaky and stashes

Spec: `.scratch/waiver/PRD.md`.

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
- Sleeper gives an IR player the status Inactive, so the pool leaves him out. A stash today is Out, PUP, Sus, or NA with the status Active.
- The injury report has no return field. Its return week is the first week after N with a status that does not keep him out. It gives one only once a later report is out.
- The build reads the slow sources with week N + 1, as the trade analyzer does. The depth chart is the latest one in the cache.
- `behind_injury` wins over `usage_rise`, and `return` wins over `handcuff`, when both rules hold.
- The handcuff rule covers QB, RB, WR, and TE, as the ticket says, not RB only as the trade analyzer does.
- The story fact sits on the sneaky and stash entries only. Best adds and trending carry no reason and no story fact.
