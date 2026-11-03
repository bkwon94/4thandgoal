# 07: Best adds and top performers

**What to build:** the Best Adds chapter lists the top three adds by points scored for the team after the add, with the projection over the same span. The Top Performers chapter lists the top five players by points scored while started for the team, with the total and the points per game started. Both chapters show headshots. Both repos.

**Blocked by:** 01 The past week keeps every rostered player, 03 The routes, the index, the hero, and the menu

**Status:** done

- [x] Each entry carries the best adds: the player, the week of the add, the points since, the projection since, and the games. A free agent pickup is an add. A drop and a re-add counts from the last add. Ties break by the earlier add.
- [x] Each entry carries the top performers: the player, the position, the total, the games started, and the points per game started. A player traded away keeps his starts.
- [x] The managers module tests cover a short stint add, a re-added player, and a traded player.
- [x] A roster with no adds reads "No adds yet." in the chapter.
- [x] The two chapters read like the Position Leaders rows: headshot, name, one emphasis per line.
- [x] The page tests read the rows in order. All checks pass in both repos.
