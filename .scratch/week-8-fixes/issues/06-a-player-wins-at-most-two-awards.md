# 06: A player wins at most two awards

Spec: `.scratch/week-8-fixes/PRD.md`, part 2. Brian's decision on 2026-11-03: "cap of two is fine".

**What to build:** Ticket 02 let each award pick its own winner, and Joe Burrow took three tiles in week 8:
Game Changer, Top Scorer, and Overachiever. A player now wins at most two. Once a player holds two awards, the
later awards skip him and take the next player. The awards keep their pick order.

**Blocked by:** none.

**Status:** ready-for-agent

- [x] Find the pick order of the awards in `awards()` of `src/cornerstone/facts_league.py` and the expected awards in `facts_nflverse.py`. Name the order in the close comment.
- [x] A player with two awards is skipped by every later award. The cap is one tunable `AWARDS_PER_PLAYER = 2` in `tunables.py`, with a comment that says why two: a reader expects the top scorer to be the top scorer, and three tiles for one player reads as a bug.
- [x] A test shows a player who leads three awards wins the first two and the third goes to the next player.
- [x] A test shows a player who leads two awards wins both.
- [x] The week 8 awards from the saved raw data: Burrow holds Game Changer and Top Scorer, and Overachiever goes to the next player. Name him in the close comment.
- [x] `make golden` ran, and the golden diff is named in the close comment.
- [x] `make check` passes.
