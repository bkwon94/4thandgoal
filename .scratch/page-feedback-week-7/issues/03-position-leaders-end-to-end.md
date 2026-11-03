# 03: Position leaders, end to end

**What to build:** A manager opens a week page and sees a Position Leaders section after Awards and before Trades. It shows five boards in the order QB, RB, WR, TE, DEF. Each board lists the three started players with the most points at that position, league wide, with rank, player name, NFL team, points, and the fantasy team that started him. A blurb from the writer sits under the boards and names only the leaders and their fantasy teams. The markup is correct and uses the existing style tokens. The design pass is ticket 04.

**Blocked by:** None (can start immediately)

**Status:** done

- [ ] The week data holds a list of position leaders. Each leader holds the player line, the position, the rank 1 to 3, the count of started players at that position, and the roster id.
- [ ] FLEX players count at their real position. Bench players do not count. The sort is points descending, then name ascending. Three rows always, fewer only when a position has fewer than three started players.
- [ ] The sheet has one fact per leader with an ID such as `LEAD.RB.1`. The text names the player with position and NFL team, the points, the rank, the count at the position, and the fantasy team. Every number in the text is in the numbers list.
- [ ] A chapter `position_leaders`, title "Position Leaders", cites the `LEAD.` facts only, with a range of 2 to 4 sentences, scope teams every roster, scope players the leaders. It sits after `awards` and before the first `trade_` chapter.
- [ ] The page has a "Position Leaders" section with five boards and 15 rows. Each row shows the rank, the player name, the NFL team, the points, and the fantasy team. The blurb renders under the boards.
- [ ] Tests at the bundle seam cover the leaders list, the facts, and the chapter position. Tests at the render seam cover the section, the five boards, and the rows.
- [ ] `uv run pytest -q` passes.
