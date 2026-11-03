# 05: Season So Far

**What to build:** the Season So Far chapter shows the points line, the bench points, and the awards shelf. The points line draws the team's points per week against the league median with a dot per week, filled for a win and hollow for a loss. The bench points line reads the season total and the worst week with the player that sat. The awards shelf shows four counts. Both repos.

**Blocked by:** 01 The past week keeps every rostered player, 03 The routes, the index, the hero, and the menu

**Status:** done

- [x] Each entry carries the points per saved week with the median of that week and the head-to-head result.
- [x] Each entry carries bench points: the season total, and the worst week with the player that sat and his points. The best lineup reads the roster slots of the current league file and the real points.
- [x] Each entry carries the awards shelf: the counts of Top Scorer, Most Valuable Benchwarmer, Game Changer, and Underperformer from the saved facts of the weeks a report ran.
- [x] The managers module tests cover a week with a known best lineup and a season with no awards.
- [x] The points line is an inline SVG that scales to the column at each tier, with the first and the last week as the only labels. It reads in both themes.
- [x] A zero count on the shelf shows in the quiet color.
- [x] The page tests read the dots, the bench line, and the four counts. All checks pass in both repos.
