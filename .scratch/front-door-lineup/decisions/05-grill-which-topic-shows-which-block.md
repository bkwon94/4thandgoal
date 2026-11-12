# 05: Which Topic Answer shows which block?

Map: `.scratch/front-door-lineup/MAP.md`.

**Kind:** grill

**Blocked by:** 04

**Status:** done

## Question

Decision 01 puts the blocks in the Topic Answers too. The spec needs the map from each of the 14 Topics to its blocks, and where each block is built. The 7 league Topics come from the weekly build in `topics.json`, so their blocks change the pipeline. The personal Topics and the trade Topics build live on the API. The spec also needs to know whether a Topic Answer may show more than one block.

## Decision

Brian decided each item on 2026-11-12.

1. A Topic Answer shows one block. The text is optional: an Answer may be a block and no text.
2. The NFL game card shows only in a free answer, such as "How does the Bears game look?". It does not go inside a lineup row, because a card that tall moves the other rows, and decision 03 keeps them still.
3. The spec has 15 blocks: the 13 of decision 01, plus the waiver list and the sell list. Waiver targets and Sell high show a list today, so text only would take rows away from them. Both lists take the Ledger look: one row per player, and the why or the bullets open in place.
4. The map of the Topics:

| Topic | Block | Where it is built |
| --- | --- | --- |
| Week recap | recap card | weekly build |
| Your last matchup | matchup card, final scores | weekly build |
| Your next matchup | matchup card, projected scores | the API, live |
| Power rankings | rank mover list | weekly build |
| Playoff race | standings ladder | weekly build |
| Your season | schedule strip | weekly build |
| Position leaders and recent trades | no block: the text, with the leaders as a list | weekly build |
| Waiver targets | waiver list | the API |
| How you stack up | slot rank bars | the API |
| Weak spots | bye grid | the API |
| Sell high or buy low | sell list | the API |
| Trade ideas | trade card, one row per offer | the API |
| Trade check | trade card | the API |
| Start or sit | lineup block | the API |

5. Position leaders and recent trades has no block. Its fact and its rows are the top scorer at each position, and the trades are only a count. No block shows players by position, and a markdown list in the text does.
6. The trade card of Trade ideas holds every offer. Each offer is one row with the partner and the gist. The first row opens on arrival into the full card of decision 04, and a tap opens another.
7. The weekly build writes the block data of the six league Topics with a block into `topics.json`, beside `fact`, `stats`, `rows`, and `text`. The matchup card of Your next matchup is built live on the API from the Sleeper projections, because its projections and win odds change through the week. The rest of that Topic still comes from the weekly build.
8. The two-player comparison block shows for a typed "Start A or B?", as decision 01 says. A free answer may show any of the 15 blocks.
