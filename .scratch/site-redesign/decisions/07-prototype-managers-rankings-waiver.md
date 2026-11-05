# 07: What do the managers, rankings, and waiver pages look like?

Map: `.scratch/site-redesign/MAP.md`.

**Kind:** prototype

**Blocked by:** 03, 04

**Status:** done

## Question

These three routes show tables and lists. Settle one pattern for a table, a ranked list, and a manager card in the look. Use only the published data. Add each idea that needs new data to the OUT OF SCOPE list of the map.

## Decision

The rankings page uses board "Rankings 1 · Ladder". The managers index and the manager page use board "Managers 1 · Cards", with the W/L strip of board "Managers 2 · Table" in the hero. Brian chose this on 2026-11-05, on the canvas https://claude.ai/artifact/4cFaYVh4Sm9Cw68G7FEds8. He agreed with Claude's recommendation.

The rankings page, in this order:

1. The hero: the team at rank 1, with a big "01", the team name, the record, and the movement. Under it are three tiles, Playoff, Bye, and Seed, then the blurb.
2. The ladder: the week chips, then one card for each other team. A card shows the rank, the avatar, the name, the record with the movement, and the playoff odds with a short bar.
3. A tap on a card opens four tiles with the ranks of Stand, Form, Sched, and Pts. Then come the blurb and a link to the manager page.
4. A note says how the four parts make the rank.

The managers index:

- One card for each team, in standings order. A card shows the avatar, the name, the record, the power rank, the playoff odds, and the grade letter in a box. The grade text, such as "Deep at TE. Thin at WR.", sits under it.
- The whole card is a link to the manager page.

The manager page, in this order:

1. A back link to all managers.
2. The hero: the avatar, the name, the record, and the owner. The grade letter is the big hero number, with the grade text beside it. Then come three tiles, Playoff, Bye, and Seed, and a W or L chip for each week.
3. The five chapters of the code, in their order: Season So Far, Roster, Best Adds, Top Performers, and Moves.
4. Season So Far shows a line of the points of each week against the dashed median line. A filled dot marks a win. Three tiles show the points for, the record against the median, and the high week.
5. Roster shows a tile for each position slot, with its rank and its depth, then the four grade parts with their weights and ranks.
6. Best Adds and Top Performers show each player in a round photo frame, with the points on the right.
7. Moves shows three tiles, adds, drops, and trades, then each week as a row of its adds, drops, and trades.

One pattern for each kind:

- **A ranked list** is a column of cards on the phone, with the rank in mono type on the left and one number on the right. A tap opens the detail inside the card. The rankings page and the managers index both use it.
- **A table** stays only where it has five columns or fewer, such as the standings of the week page. Brian and Claude rejected the dense table of board "Rankings 2 · Board": eight columns at phone width give small cells and 12px text.
- **A manager card** shows the avatar, the name, the record, one key number, and the grade box.

Brian rejected board "Rankings 3 · Movers", because it shows some teams up to four times and puts the full ranking far down the page. He rejected board "Managers 3 · Profile", because its two-column tiles cut long team names and its centered hero breaks the left alignment of the look.

The waiver page is out of scope. No client takes the `waiver` package, so no client builds the page, and Brian cannot judge it on screenshots. Brian chose this on 2026-11-05.

The boards showed one fact. The managers file has no player list for each roster, so the Roster chapter shows the rank of each position slot, as the code does now. All the boards use only the published data, so the list of ideas that need new data stays empty.

The prototype lives on the canvas, not in the repo, so no prototype code needs a delete.
