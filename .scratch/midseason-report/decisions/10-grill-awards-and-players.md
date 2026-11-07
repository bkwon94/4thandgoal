# 10: Which awards, top performers, and players to watch does the report name?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** grill

**Blocked by:** 05, 06

**Status:** done

## Question

The report names top performers across all teams, midseason awards, and players to watch for the second half. The spec needs: the list of awards and the fact behind each one, the rule of a top performer, for example by position or overall, and the rule of a player to watch. The roast rules of the map apply to each award.

Brian added on 2026-11-05: the report also shows the top 10 at each position, not only the top performers overall. The grill decides the positions, the measure, and the look.

## Decision

Brian decided it in the grill on 2026-11-05.

Position top 10:

- The positions are QB, RB, WR, and TE in both leagues, plus DEF in CPC only. Neither league starts a kicker, and NorCal starts no DEF.
- The measure is total points in the league's own scoring, weeks 1 to the report week. Points per game sits beside it.
- The pool is every NFL player, rostered or not. Each row shows his manager now, or a "Free agent" tag in the brand red.
- One position shows at a time, with a switch at the top. It opens on RB. A row has the rank, the headshot, the player, his NFL team, the points, the points per game, and the manager's avatar. The #1 row is larger.
- The top performers chapter is the Position top 10 chapter. The report has no overall list, because one list across positions ranks unevenly. Top performers keeps its meaning on the manager page.

The awards: seven, each from one fact that it shows. No award repeats the #1 of another chapter, so the record book, schedule luck, and the draft chapter keep their own headlines.

1. **MVP:** the started player with the most Points over the line, at QB, RB, WR, or TE.
2. **Streaming king:** the manager whose streamed QB or DEF starts scored the most, as ticket 03 named it.
3. **Bench crime of the year:** the single week with the most bench points that a better lineup would have turned into a head-to-head win.
4. **Heartbreak of the year:** the closest head-to-head loss.
5. **Beatdown of the year:** the biggest head-to-head margin.
6. **Most active:** the most adds and trades.
7. **Set and forget:** the fewest moves. A good record makes it a compliment, and a bad record makes it a roast.

Players to watch: three lists of 3 players per league. Each player shows his manager.

- **Due to rise:** rostered QB, RB, WR, and TE with the largest Expected gap under zero.
- **Due to fall:** rostered QB, RB, WR, and TE with the largest Expected gap over zero.
- For both lists, the gap averages over the whole season, not the Expected window, and a player needs 4 games or more.
- **Grab him now:** the free agent with the highest projection for the rest of the regular season, from `projections_ahead.json`.
