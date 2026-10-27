# Roster fit reads depth by position rank

Roster fit read only the best lineup's points per game before and after a trade. A side could trade
its two starting running backs for two receivers and lose nothing on paper, because the lineup total
moved less than the threshold while the RB2 slot fell to a player no one would start. Brian asked for
depth per position, strength per position, and the holes a trade opens. We now read all three against
one line: the position rank, a player's place at his position among every player with a stat line,
rostered or not, by lineup value. The line is rank 36 at RB and WR and rank 24 at QB and TE. A slot
below the line is a hole. A new hole with no lineup gain is one step down. A lineup gain that opens a new
hole is no step, because the two cancel. The highest-value player step with a new hole is no step too.
Depth and strength are facts for the reason and the analysis, never a step. The handcuff block narrows
to a lineup loss, so a side that trades its starter for the backup and opens a hole steps down.

## Considered Options

- The best free agent at the position as the line: a sentence a reader can check on the waiver page.
  Rejected because the floor moves with one pickup, and a thin waiver wire says nothing about whether
  the side still has a starter. He stays in the reason as the best free agent and his rank.
- A fixed points-per-game floor per position: stable but arbitrary. Rejected because no one can say
  why 7.0 and not 8.0.
- The league's worst starter per position: measures the other eleven rosters, not this one. Rejected
  because it needs a league-wide read on every grade and the reader cannot check it.
- A depth adjuster of its own: rejected because the rubric caps every adjuster at one step, and two
  reads of the same roster would double-count a lineup loss.

## Consequences

- The rank pool is the whole league, so RB24 means the 24th running back in the NFL by lineup value
  over the known games, not on 12 rosters. A free agent is in the pool.
- The rank per position computes once per snapshot. The finder grades about a thousand trades per
  call and must not rank the league per side.
- The grade cache key must hash the free-agent inputs the rank and the best-free-agent read use.
- The snapshot gains the free agents' status fields, which the live path drops today.
- A starter due back inside the 3-week bye window reads as a bye until he returns. One due back later
  is a hole. His lineup value still counts his projection ahead. Superseded by ADR 0004: the window is
  the return window, and a bye is no longer a hole.
- A bench player whose own bye falls in the starter's bye week cannot cover him, because both miss that week.
  Superseded by ADR 0004: a bye needs no cover.
- The week 6 hand-worked trades can move. Each moved grade needs Brian's word before merge.
