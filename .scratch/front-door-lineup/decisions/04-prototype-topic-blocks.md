# 04: What do the blocks of the other Topics look like?

Map: `.scratch/front-door-lineup/MAP.md`.

**Kind:** prototype

**Blocked by:** 03

**Status:** done

## Question

Nine blocks serve the other Topics: the matchup card, the schedule strip, the standings ladder, the slot rank bars, the trade card, the rank mover list, the bye grid, the transaction feed, and the recap card. The spec needs the look and the fields of each, in the same visual language as the blocks of decision 03.

Build each one with real data of both leagues. Search scrolltide first. Use the design bar of decision 03. Give the prototype its own port, not 3000 or 8090.

## Decision

Brian chose variant B, Rows and marks, on 2026-11-12, on his iPhone. He turned down A, Rows (text rows only), and C, Glance (one sentence and one mark, with the rows behind "More").

Each block keeps the Ledger rows of decision 03. A row with detail shows a chevron, opens taller in place, and its detail comes into focus from a blur. Each block also carries one small mark:

1. Matchup card: a tug bar for the win odds, and the two lineups slot by slot, with a bar from the center line for the gap in each slot.
2. Schedule strip: a dashed step path of the opponent ranks over the weeks left, drawn against the playoff line. The rows under it show the week, the opponent, the rank, and the record.
3. Standings ladder: one row per team with the rank, the name, a bar of the playoff odds, and the record. A rule marks the playoff line. The row of Your team is red.
4. Slot rank bars: one row per slot with a bar from the league middle, worse to the left and better to the right, and the rank "6th of 12". The header holds the roster grade and a one-line read.
5. Trade card: the two sides, each player with a bar of his projected points for the rest of the season, and a tug bar of the two totals. The edge closes the card: "Edge: To Infinity and Bijan, +77.4."
6. Rank mover list: one row per team with the rank, the name, a bar from the center for the move, and the arrow with the number of places.
7. Bye grid: a dot matrix of the starters and the bench against the next weeks. A red dot marks a starter on a bye.
8. Transaction feed: a strip of the moves per day over the header, then one row per move, newest first. A dot marks the kind: trade, waiver, or free agent. A trade row shows what each side got.
9. Recap card: the score, a strip with a mark for each team and a tick for the league median, the top scorer against his projection, and the first sentence of the recap.

The colors are the colors of decision 03: red for Your team or the side that wins, gray for the rest, and the up and down colors of the site for a move.

Brian's words: "B is nice." He gave no other reason. In B, the marks show the shape of the data, and the rows still hold every number.

The prototype found four data gaps. Decision 11 settles them:

- No file holds the win odds of one game. The prototype got them from the gap of the projected totals and the league `spread` in `sim.json`.
- No file holds a trade grade, because the analyzer computes it live on the API. The prototype showed the edge in projected points for weeks 10 to 17.
- The roster grade ranks only QB, RB, WR, and TE. It has no rank for FLEX or DEF.
- norcal has no league median (`median` is null in `page.json`). The recap hides the median tick there.

The data of each block in the prototype:

| Block | Files |
| --- | --- |
| Matchup card | `raw/matchups_next.json`, `raw/projections_ahead.json`, `raw/players.json`, `page.json` |
| Schedule strip | `raw/matchups_next.json`, `raw/schedule.json`, `page.json`, `rankings.json` |
| Standings ladder | `page.json`, the odds in `facts.json`, `settings.playoff_teams` of `raw/league.json` |
| Slot rank bars | `managers.json` |
| Trade card | the trades in `managers.json`, `raw/projections_ahead.json` |
| Rank mover list | `rankings.json` |
| Bye grid | `raw/matchups_next.json`, `data/nfl/cache/nflverse/games.csv` (a gitignored cache) |
| Transaction feed | `raw/transactions.json`, `raw/transactions_prev.json` |
| Recap card | `page.json`, `topics.json` |

The prototype code is deleted.
