# A bye is not a hole, except this week for a middle team

ADR 0003 made a starter's bye inside a 3-week window a hole when no bench player above the line covered
him. On week 7 live data that flagged 13 uncovered byes across 12 rosters, and the finder found 0 win-win
trades where the old rule found 5. Brian ruled that a bye is something a team handles, not a reason to
grade a trade down. The one bye that costs a team is the one it cannot handle: a team in the race for the
last playoff spot gets a player who starts for it and sits out this week. So a bye is never a hole, with
one exception. For a middle team, a player it gets who starts after the trade and has his bye in the trade
week is a new hole, and the roster fit step rule runs as for any new hole. The window stays at 3 weeks for
a starter due back, and its name is now the return window.

## Considered Options

- Keep the bye kind and set the window to the trade week only. Rejected because the cover read still
  swayed the grade for every team, and a contender or a seller does not need this week's win.
- Any team that is not a contender, so a seller too. Rejected because the standing adjuster already tells
  a seller to sell, so this week's win is not its goal.
- A flat one step down, or a reason sentence only, in place of a new hole. Rejected because the hole rule
  already weighs a hole against a lineup gain, and a second rule would double-count.
- A lean in the schedule adjuster, which counts byes left. Rejected because byes left is a season fact for
  both sides, and this is one Sunday cost for one team.

## Consequences

- The two bye bullets in ADR 0003 Consequences are superseded by this ADR.
- No bench cover cancels the exception. The player it gets either starts on his bye week or he does not.
- A player a side gives who has his bye in the trade week counts for nothing on either side.
- With no schedule map, the exception reads no hole, and the reason says the schedules are not available.
- The schedule adjuster keeps its byes left lean. Two different facts, one owner each.
- Cached grades change, so `DOCUMENT_VERSION` moves to 10.
- The week 6 hand-worked trades do not move: the holes that moved them under ADR 0003 are out starters,
  not byes.
