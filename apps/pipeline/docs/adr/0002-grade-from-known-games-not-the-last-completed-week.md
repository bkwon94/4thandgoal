# Grade from the known games, not the last completed week

A grade read every input through week N-1, so a Thursday night game touched no grade until the
Tuesday build. Brian trades during the week, after a Thursday game or on a Sunday night, and the
grade must see those games. We now bound every player stat at the known games: weeks 1 to N-1 plus
every week N game that has a stat line on Sleeper, final or in progress. A game in progress counts,
and the stamp and each factor reason that reads it say so. The standings and the chart week still end
at week N-1, because a record changes once a week and the chart reprices once a week.

## Considered Options

- Final games only, with final as kickoff plus 4 hours 30 minutes: no live source says a game is
  final. Rejected because a 3:45 pm Sunday grade would hide the whole 1 pm slate in its fourth quarter.
- A live scoreboard source for game status: exact, but a fourth live source for one label. Rejected
  while the kickoff rule gives a good enough label.
- Keep week N out and refresh on Tuesday only: rejected, because that is the gap Brian named.

## Consequences

- A grade can swing during a game. The in-progress label puts that on the reader, who can see the
  game is on.
- Sleeper posts Sunday snap counts on Monday, so snap share is pending for a day. A pending count
  never reads as zero.
- The grade cache must key on a hash of the week N stat lines, or a Wednesday grade serves all week.
- The nflverse injuries and player weeks files refresh every 6 hours, so a Monday grade sees the
  Sunday WOPR by morning.
- A player tagged Out with no week in the returns file takes his projection ahead as lineup value, as
  if due back at week 14, so an in-game injury drops his value the same day.
