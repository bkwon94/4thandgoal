# packages/midseason/site/act-two: the chapters of Act II, "The moves"

## Knows

- Draft steals and busts: the cost against the points at the position and the tag of each bust.
- Waiver hits and misses: the hits by Points over the line, the misses, the outbid claims, and the streamers.
- The trade report card: the top 3 trades as full cards with the record of each team since the trade, then every
  other trade as a short row of two quiet lines. Each result with a winner names the team, as "Slight edge to <team>".
- The record book with the awards. Heartbreak sits on the closest game and Beatdown on the biggest margin, so each
  game shows once.
- Quick hits, the last chapter: one block with two parts, each under a level 4 heading with its own prose.
  - Lineup choices: the Bench points of each team and each loss that its best lineup would have won.
  - The injury toll: the starter games each team lost, with its key starters.

## Ports

- `report/chapter-part.tsx` picks each part by the key of its chapter.

## Does not do

- It computes no fact, no result, and no award. The pipeline writes them into the midseason file.
- It reads no file, no env, and no config (ADR 0012).
