# 01: Which measure ranks players inside the grade

Map: `.scratch/grade-clarity/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The Position rank sets the line and the holes of roster fit. Today it sorts by points per game over the last `LINEUP_WEEKS` (4) weeks, counting only the games played. One big game in a short window moves a player about 40 spots, as Omar Cooper at WR18 shows, when Sleeper has him at WR60 by total points.

The research compares four measures at week N against the points of weeks N+1 to N+4, over weeks 1 to 8 of this season, with real data:

1. Points per game over the last 4 weeks, as now.
2. Season total points.
3. Season points per game.
4. The Sleeper projection of the rest of the season.

The spec needs the one measure the grade uses, and the reason. Brian's bet from the grill is season points per game, with the trend adjuster to carry recent form.

## Decision

The Position rank inside the grade sorts by season points per game, counting only the games played. Brian decided it on 2026-11-05, from the research in `01-research-rank-measure.notes.md`.

- It predicts the next weeks as well as the 4-week measure. The hit rate above the line differs by 0.06 or less at each position.
- Players move 2 to 3 times less from week to week. At WR the mean move is 4.0 spots, against 12.1 for the 4-week measure.
- It does not reward a small sample. At week 8 the 4-week measure puts 9 WRs with 2 games or fewer above the line, and season points per game puts none.
- Season total points counts a missed game as a zero. The due-back and out-for-season steps already handle absence, so the total is not used.
- Omar Cooper Jr. is WR18 by the 4-week measure, WR26 by season points per game, and WR60 by season total, as Sleeper shows.

The due-back and out-for-season rules of `lineup_value` stay. The spec changes the definitions of "Lineup value" and "Position rank" in `GLOSSARY.md` when the code changes.

Limits: only weeks 1 to 8 are complete, and the Sleeper rest-of-season projection had 2 test weeks, too few to judge. At QB the season total scored best, by about 2 players of 24.
