# packages/midseason/site/act-two: the chapters of Act II, "The moves"

## Knows

- Draft steals and busts: the cost against the points at the position, the tag of each bust, and the one that got away.
- Waiver hits and misses: the hits by Points over the line, the misses, the outbid claims, and the streamers.
- The trade report card: the top 3 trades as full cards with the record of each team since the trade, then every
  other trade as a short row. A player out in the first week after his trade has the tag "Hurt on arrival".
- Lineup choices: the Bench points of each team and each loss that its best lineup would have won.
- The record book with the awards. Heartbreak sits on the closest game and Beatdown on the biggest margin, so each
  game shows once.

## Ports

- `report/chapter-part.tsx` picks each part by the key of its chapter.

## Does not do

- It computes no fact, no result, and no award. The pipeline writes them into the midseason file.
- It reads no file, no env, and no config (ADR 0012).
