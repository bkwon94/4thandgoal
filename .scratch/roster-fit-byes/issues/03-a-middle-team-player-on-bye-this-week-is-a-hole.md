# 03: A middle team's player on bye this week is a hole

**What to build:** For a middle team, a player it gets who starts after the trade and has his bye in
the trade week is a new hole. The race comes from the standing read: contender, seller, or middle. No
bench cover cancels the hole. The hole sentence reads "<slot> is a hole after the trade: <name> has
his bye in week <N>, and a middle team needs the win." The roster fit step rule runs as for any new
hole: one step down with no lineup gain, no step with a gain, no step up for the highest-value player.
A contender or a seller reads no bye hole. A player who lands on the bench is no hole. A bye in week
N+1 is no hole. A player the side gives on bye counts for nothing. With no schedule map, no bye reads
and the reason names the missing schedules.

Every test runs through the grade seam on the slow snapshot and reads the roster fit adjuster's step
and reason. The fixture trade week is 6. Rosters 7, 8, 10, 11, and 12 are middle teams, roster 4 is a
seller, rosters 1, 5, and 6 are contenders. Move a team's bye to week 6 with the bye helper to make
the case.

**Blocked by:** 02, A bye is never a hole.

**Status:** done

- [x] A middle team gets a player who starts and has his bye in week N: step -1, reason names the slot, the player, week N, and the race.
- [x] The same trade for a contender reads no hole.
- [x] The same trade for a seller reads no hole.
- [x] The same trade with the bye in week N+1 reads no hole.
- [x] The same trade where the player lands on the bench reads no hole.
- [x] The same trade with a lineup gain reads step 0 and the reason names the hole.
- [x] A middle team gives a player with his bye in week N and the reason does not name him.
- [x] With no schedule map, the trade reads no hole and the reason names the schedules.
- [x] The hand-worked table passes with its letters unchanged. If a row moves, stop and report it.
- [x] The finder timing test stays under 5 seconds.
- [x] The full suite passes and ruff is clean.
