# 01: Does the sim page keep its name?

Map: `.scratch/playoff-paths/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The page now answers what each team needs to reach a Goal, and it holds the League board. "Season sim" names the replay, not the paths. Decide if the page keeps the name "Season sim" or takes a new one, such as "Playoff picture" or "The race". Decide also if the route `/sim/<season>/` stays. The name sets the copy of the Announcement, the menu item, the Sim tile, and the front door push, so the prototype needs it first.

## Decision

The page takes the name "The Race", with a capital R, and the short label "Race" in the menu and the shell. The route stays `/sim/<season>/`, so old links from the Announcement of `season-sim` and the week tiles keep working. The code keeps the package name `sim`, and the docs keep "the sim page". The replay inside the page keeps its button names, such as "Sim the season". The new name gives the Announcement of the release its hook: "The Race is on." Brian chose option B, 2026-11-24. "Season sim" only named the replay, "Playoff picture" is long for the menu, and "Playoff paths" reads flat.
