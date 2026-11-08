# 04: Which tiles become Trend tiles, and what does each trend plot?

Map: `.scratch/card-polish/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

`Tile` holds the four week numbers on the week page and on home, and numbers on the manager hero, Roster, and Moves. The manager hero is out of scope. `managers.json` gives the points, the median, and the result of each week. The week page needs the earlier `page.json` files of the season. The spec must name each Trend tile and the number its line plots.

## Decision

Brian decided on 2026-11-07. Seven tiles become Trend tiles. Each trend runs from week 1 to the week of the page, one point per week, so an older week page never shows a later week.

| Tile | Plots, one point per week | Chart |
| --- | --- | --- |
| Top score (week numbers) | The top score of the week | Bars, the page week lit |
| Median (week numbers) | The league median of the week | Stepped area |
| Closest (week numbers) | The margin of the closest game | Bars, the page week lit |
| Game Changer (week numbers) | The points over projection of the Game Changer | Bars, the page week lit |
| Adds (Moves) | The adds of the manager | Bars |
| Drops (Moves) | The drops of the manager | Bars |
| Trades (Moves) | The trades of the manager | Dots, because most weeks are 0 |

The chart types follow the Lime Metrics item: a bar series and a stepped area. Its donut is out, because none of the seven numbers has parts of a whole.

The tiles of Season So Far stay plain, because the points line above them already shows the trend. The tiles of Roster and of the rankings have no series. The hero tiles belong to `hero-slots`.

The week numbers read the earlier `page.json` files of the season at build time (map decision, site only). Moves reads `moves.weeks` of `managers.json`.

## Comments

2026-11-07, during the acceptance tests: only weeks 6 to 8 of CPC and week 8 of NorCal are published, so the earlier `page.json` files cannot give a trend from week 1. Brian chose five Trend tiles on the site only. Top score and Median read every week from `managers.json`: the top score is the highest points of the week, and the median is the published median of the week, or else the median of the points of every team with the rounding rule of the week numbers. Adds, Drops, and Trades read `moves.weeks`. Closest and Game Changer stay plain tiles, because `managers.json` has no pairs and no projections. A later pipeline spec can add a season series for them, and the Trend tile takes it with no change.
