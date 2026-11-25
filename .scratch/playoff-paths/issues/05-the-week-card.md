# 05: The week card: the Score to beat, the root-for list, and the result tiles

Spec: `.scratch/playoff-paths/PRD.md`. Acceptance tests AT-14, AT-15, AT-16, AT-18, AT-35, AT-36, AT-37, AT-42, and AT-43.

**App:** both

**What to build:** Under the Finish list, the week card shows the Score to beat against the opponent and the median, "to win" and "to be sure", then the four result tiles (two for NorCal), then the root-for list of every other game for the chosen result. Each row shows both results with their odds. A game under 1 point has a gray "Doesn't matter" tag. Median rooting shows for 1 or 2 teams. The tiebreak gap shows when close. A tap on a tile sets a What-if. With the API down, the page shows the file and a quiet note.

**Blocked by:** 04

**Status:** in-review

- [x] The Score to beat of Bo Girds for week 12 holds 2 scores against Teez Nuts and 2 against the median, each 80% score above its 50% score.
- [x] Each of the 4 results holds 5 root-for rows.
- [x] A tap on a result tile changes the Finish list and the board to the numbers of the response.
- [x] NorCal shows 2 tiles and no median score.
- [x] The week card passes the WebKit overlap check at the 4 sizes, in light and dark mode.
- [x] `make check-fast` passes.
