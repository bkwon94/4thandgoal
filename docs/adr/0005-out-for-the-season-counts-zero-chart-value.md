# A player out for the season counts zero chart value

The start letter of a side is the ratio of the chart value it gets over the chart value it gives, and the chart keeps a star's value through an injury. A manager who trades for an injured star with no return week buys the upside, so the rubric credits that bet. A manager who trades for a player out for the season buys nothing, so that player counts zero chart value for the side that gets him, and the injury adjuster steps that side down once more. We chose the returns file's `season` mark as the only sign of a season-ending injury, because Sleeper's IR status does not mean out for the season and players return from it.

## Consequences

- The commissioner's returns file is the source of truth. A season-ending injury the file does not mark reads as a star return bet, and the grade credits it.
- The zero counts on the side that gets him only. The side that gives him still gives his full chart value, so the fairness reads lopsided on its own.
- He also counts zero lineup value on every side, because he cannot play. The side that gives him loses nothing in its lineup, and the side that gets him gains nothing.
- The cache key holds the set of players out for the season, so one edit of the returns file changes the next grade.
