# Roster fit reads depth, strength, and holes by position rank

**Status:** ready-for-agent
**Date:** 2026-10-26
**Decision record:** `docs/adr/0003-roster-fit-reads-depth-by-position-rank.md`
**Glossary:** "Position rank", "The line", "Hole", "Depth", "Strength", "Handcuff" in `GLOSSARY.md`

## Problem Statement

Brian grades a trade that sends his RB1 and RB2 away for two receivers. The best lineup moves less than
3 points a game, so roster fit says the lineup stays about the same. His RB2 slot now holds a back no
one would start. The grade does not see it. The same blindness runs the other way: a trade that splits
a stud receiver into one back and one receiver can fix a hole at RB, and the grade sees only the
lineup total. Roster fit reads one number, the best lineup's points per game, and nothing of the bench,
the depth at a position, or the byes ahead.

## Solution

Roster fit still gives one step, from three reads of the side's roster before and after the trade.

1. The best lineup, as today.
2. Depth and strength per position, against the line. A player's position rank is his place among
   every player at his position with a stat line in the known games, rostered or not, by lineup value.
   The line is rank 36 at RB and WR and rank 24 at QB and TE. Depth is the count of the side's
   players at a position above the line. Strength is how many of RB1, RB2, WR1, and WR2 hold a rank
   of 24 or better.
3. Holes. A hole is a starting slot that holds a player below the line, or holds no player. A bye
   hole is a slot whose starter has his bye in the next 3 weeks and no bench player above the line
   can cover. A starter due back inside that window reads as a bye until he returns. A starter due
   back later is a hole.

The step: a lineup loss or a new hole is one step down. A lineup gain with no new hole is one step
up. The highest-value rule stays, and a new hole blocks it. A gain that opens a new hole is no step,
and the reason names the hole. A handcuff still blocks a step down for a lineup loss, and never for a
hole. The one-for-two rule stays as today.

The code writes one short fit reason: the step and the one fact that drove it. The slot each new
player takes, the player he pushes out, the depth and strength counts, and the best free agent at a
hole's position with his rank all go to Claude as cited facts. Claude's side analysis is where the
reader gets the natural read. K and DEF stay out of the three new reads.

## User Stories

1. As a manager who grades a trade, I want roster fit to see that my RB2 slot falls below the line
   after I trade two backs away, so that a thin lineup costs the grade a step.
2. As a manager, I want a trade that fills a hole at RB with a real starter to count that fill, so
   that a split of my stud receiver into a back and a receiver grades on what it fixes.
3. As a manager, I want the reason to name the slot each new player takes and the player he pushes
   out, so that I can see the lineup move in my head.
4. As a manager, I want to know how many of my RB1, RB2, WR1, and WR2 sit inside the top 24 before
   and after, so that I can see whether the trade weakens a position without a hole.
5. As a manager, I want the depth count per position before and after, so that I know how many
   starters I have left at RB when one gets hurt.
6. As a manager, I want a bye in the next 3 weeks with no cover to count as a hole, so that a trade
   does not leave me with an empty slot on Sunday.
7. As a manager, I want a bench player above the line to cover a bye, so that a bye with a real
   backup is no hole.
8. As a manager, I want a starter due back in 2 weeks to read like a bye, so that a trade for a player
   out now does not hide an empty slot this week.
9. As a manager, I want a starter due back in 6 weeks to read as a hole, so that his projection ahead
   does not fill a slot he cannot play.
10. As a manager, I want a hole that was there before the trade to give no step, so that the grade
    judges the trade and not my roster.
11. As a manager, I want a trade that opens a new hole to block the step up, even when I get the
    highest-value player, so that a lopsided lineup never earns a step for one name.
12. As a manager, I want a trade of my starter for his handcuff that opens a hole to step down, so that
    the handcuff block does not hide a missing starter.
13. As a manager, I want the best free agent at the hole's position named with his rank, so that I
    know whether waivers can fix it.
14. As a manager, I want every rank to be a league rank among all players, so that "RB24" means the
    24th back in the NFL and I can check it.
15. As a manager, I want a player with no game in the window to rank last, so that an empty stat line
    never fills a slot.
16. As a manager, I want a FLEX slot to read the line of the player's own position, so that a WR40 in
    the flex is a hole and a TE20 is not.
17. As a manager, I want K and DEF out of the depth, strength, and hole reads, so that a kicker never
    moves the grade.
18. As a manager, I want the fit reason short, with the one number that drove the step, so that the
    factor row reads in one glance.
19. As a manager, I want the analysis paragraph to weave the depth and hole facts in its own words, so
    that the page reads like a person wrote it.
20. As a manager who runs the finder, I want every found trade to read holes the same way, so that the
    finder never offers a trade that empties a slot.
21. As a manager, I want a grade to refresh when a free agent's stat line changes the ranks, so that a
    cached grade never shows a stale line.
22. As a manager, I want the week 6 hand-worked trades that move to be listed with old and new
    letters, so that I can say yes or no to each before the change ships.
23. As a manager, I want the four bounds, the line at 36 and 24, the strength bound at 24, and the bye
    window at 3, in one tunables place, so that a change is one edit.
24. As a reader of the rubric, I want the roster fit section to state the three reads and the step
    rule in plain words, so that Claude and I read the same rule.
25. As a reader of the glossary, I want "position rank", "the line", "hole", "depth", and "strength"
    to mean one thing each, so that a reason and a test use the same word.
26. As a manager, I want a saved week and a live grade to give the same ranks for the same data, so
    that the Tuesday build and a Saturday grade agree.
27. As a manager, I want a free agent who is not Active on Sleeper left out of the best free agent
    read, so that a retired name never shows as a pickup.
28. As a manager, I want a free agent on injured reserve left out of the best free agent read, so
    that a hurt name never shows as a pickup.
29. As a manager, I want the due-back note kept, so that a player due back still shows the projection
    he counts for.
30. As a manager, I want the in-progress label kept on a rank that reads a game in progress, so that
    a rank that can still move says so.

## Implementation Decisions

- **The rank table.** The snapshot gains one read, computed once per snapshot: for each of QB, RB,
  WR, and TE, every player with a stat line in the known games, in order of lineup value, with the
  position order as the tie rule and the player id last. The rank pool is all players with a stat
  line, which the snapshot already holds for rostered and unrostered players. A rostered player due
  back ranks by his projection ahead, as his lineup value says. A player with no game in the window
  ranks last. The finder grades about a thousand trades per call, so the table builds once and every
  side reads it.
- **The line and the bounds.** Four tunables: the line at RB and WR, the line at QB and TE, the
  strength bound, and the bye window. The line is a rank, so a change of the league's size is a
  change of these numbers and nothing else.
- **The free agents.** The snapshot gains, per position, the free agents who pass the waiver pool's
  eligibility rule today: not rostered, on an NFL team, Active on Sleeper, or Inactive and out as a
  stash. The live path and the saved path both build it from the raw players file minus the rosters.
  The best free agent at a position is the one with the best position rank. This read feeds a fact
  only, never a step.
- **The side reads.** The side that the adjusters read gains: its starting slots before and after,
  each with the player and his rank; the holes before and after, each with the slot, the position,
  the reason it is a hole, and the player who left it; the depth per position before and after; and
  the strength count before and after. A new hole is one in the after set and not in the before set,
  matched by slot and kind.
- **The hole kinds.** Three kinds: below the line, empty, and no cover. "No cover" is the bye kind
  and the due-back kind: the slot's starter has his bye in weeks N to N+2, or is due back in weeks
  N+1 to N+2, and no bench player at an allowed position above the line is free to cover him. A
  starter due back after N+2 is below the line for this read, whatever his projection ahead ranks.
  A FLEX slot reads the line of the player's own position. K and DEF slots are never holes.
- **The step.** A lineup loss steps down, with the handcuff block as today. A new hole steps down
  always. A new hole blocks the step up for a lineup gain and for the highest-value rule. The
  one-for-two rule stays. When both a loss and a new hole apply, the step is one down and the reason
  names the hole.
- **The fit reason.** One sentence from the code with the fact that drove the step. A new hole:
  "RB2 is a hole after the trade: Spears is RB38." A loss, a gain, the highest-value rule, the
  handcuff block, and the one-for-two rule keep today's sentences. The due-back notes stay. A rank
  that reads a game in progress carries "game in progress" as today's reasons do.
- **The facts.** The trade fact sheet gains, per side: one slot fact per player the side gets, with
  the slot he takes and the player he pushes out or "sits on the bench"; one fact per new hole with
  the best free agent and his rank; one depth fact per position whose count changes; one strength
  fact when the top-24 count changes. Each fact carries its numbers, so the analysis checker accepts
  them in the prose. The hole fact and the depth fact are the facts the reason cites.
- **The rubric prompt.** The roster fit section states the three reads, the line, the hole kinds,
  the step rule, and the narrowed handcuff block, in the glossary's words. The handcuff section drops
  the sentence that the block is broad.
- **The cache key.** The grade key and the finder key add a hash of the inputs the rank table reads
  for unrostered players: the position and the fields that give lineup value, per week in the
  window. The document version bumps to 8.
- **The document.** No new field. The factor row carries the short reason. The analysis carries the
  natural read. The site needs no change.
- **Prose rules.** "Position rank", "the line", "hole", "depth", and "strength" are the words. No
  reason says "replacement", "tier", "floor", or "gap". Every number is plain words.

## Testing Decisions

- A good test gives a snapshot and a trade and checks the step, the reason, the facts, or the key.
  It never reads a private helper. It names the slot, the player, the rank, and the number it expects.
- **The rubric seam.** `grade` on the week 6 fixture snapshot. Cases: two backs away opens an RB2
  hole and steps down; a back in for a receiver closes a hole and the gain steps up; a hole before and
  after gives no step; a new hole blocks the highest-value step; a starter for his handcuff with a
  hole steps down; a bye in the window with cover is no hole; a bye with no cover is a hole; a starter
  due back in the window reads as a bye; one due back after the window is a hole; a FLEX WR below 36
  is a hole and a FLEX TE at 20 is not; K and DEF never make a hole. Every existing fit test passes
  unchanged or with a named reason change. Prior art: the fit tests and the handcuff tests in the
  rubric tests.
- **The snapshot seam.** The rank table on the fixture: a named player's rank at RB; a player with
  no game ranks last; a due-back player ranks by his projection ahead; the live snapshot and the
  saved snapshot give the same table for the same raw. The free agents per position on the fixture,
  with an Inactive name left out. Prior art: the snapshot tests and the live tests.
- **The facts seam.** The trade fact sheet for a named trade carries the slot fact, the hole fact
  with the best free agent, and the depth fact, each with its numbers. The analysis checker accepts a
  sentence that quotes a cited rank. Prior art: the trade facts tests and the analysis tests.
- **The cache key seam.** A changed stat line of an unrostered RB changes the key. A changed stat
  line of an unrostered K does not. Prior art: the cache key tests in the API tests.
- **Real-data check.** The week 6 hand-worked trades run on the branch. The build report lists every
  grade that moves with its old and new letters. Brian says yes or no to each before merge.

## Out of Scope

- A depth table on the site. The reason string and the analysis carry the numbers.
- Claude writes a factor reason. The code writes it.
- A step for bench depth in a one-for-two trade. The rule stays as today.
- A league rank of rosters by position. Strength is a count of top-24 starters on this roster.
- A change to the waiver page, the weekly report, or the saved history.
- A change to the start letter, the chart week, or the other adjusters.
- The start-or-sit feature. Its handoff is `.handoff/cornerstone-start-sit.md`.

## Further Notes

- The week 6 fixture holds 698 stat lines, 557 of them for players on no roster, so the rank pool is
  real data with no new fixture.
- The week 6 raw folder's projections-ahead file holds rostered players only, so a free agent due
  back has no projection ahead there. His rank reads his recent points, which is what lineup value
  gives with no projection row. No test should depend on a free agent's projection ahead.
- Sleeper has no free-agent endpoint. Free agents are the players file minus the rosters, as the
  waiver pool reads them today. The live players fetch is cached for one day.
- The schedule map is None when the slow sources are not loaded. With no map, no bye hole reads, and
  the fit reason says the schedules are not available, as the schedule adjuster does today.
- The league has 12 rosters, 14 slots: QB, RB, RB, WR, WR, TE, FLEX, FLEX, DEF, and 5 bench. No K
  slot and no IR slot. The line numbers assume 12 teams.
