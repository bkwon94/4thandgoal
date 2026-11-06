# 05: What does the week page show, and in what order?

Map: `.scratch/site-redesign/MAP.md`.

**Kind:** prototype

**Blocked by:** 03, 04

**Status:** done

## Question

The week page is the main read of each Tuesday. Settle the order of the chapters, the hero, and each component in the look: the matchups and their recaps, the median, the awards, the standings, and the next week. Use only the published data. Add each idea that needs new data to the OUT OF SCOPE list of the map.

## Decision

The week page uses the order of board "Week 1 · Story", with the four numbers of board "Week 2 · Glance" right under the hero. Brian chose this on 2026-11-05, on the canvas https://claude.ai/artifact/4cFaYVh4Sm9Cw68G7FEds8.

The order:

1. The hero: the Matchup of the Week with its reason, the margin, both teams and their top players, the share bar, and the full blurb.
2. The four numbers: the top score, the median, the closest margin, and the Game Changer gap over projection.
3. Every game: one card for each matchup, by top score, with both avatars and a share bar. A tap opens its recap.
4. Game Changer: the player in a photo frame, three tiles for scored, projected, and over, and the blurb.
5. Awards: the tiles of decision 03, then the blurb.
6. Position leaders: one chip for each position, QB, RB, WR, TE, and DEF, with the top three of the chosen position, then the blurb.
7. Trades: one card for each trade, with each side and the players it gets.
8. The median game: a bar for each team with its avatar, the line, and the blurb.
9. Standings: every team, with the playoff tick and the brand line under the last playoff spot.
10. Next week: the blurb, then one card for each game. A Must Watch card shows its reason and a brand edge. A key player on bye shows on the card.
11. The footer: the links to the past week and the next week.

Brian rejected the tabs of board "Week 3 · Tabs", because a reader often misses content behind a tab. All the chapters use only the published data, so the list of ideas that need new data stays empty.

The prototype lives on the canvas, not in the repo, so no prototype code needs a delete.
