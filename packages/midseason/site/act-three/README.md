# packages/midseason/site/act-three: the chapters of Act III, "What comes next"

## Knows

- The look ahead: each team's games left in the regular season with the record of each opponent, and the win rate of
  its opponents. The softest schedule comes first, with a tag on the softest and the hardest.
- Players to watch: Due to rise and Due to fall from the Expected gap a game, and Grab him now from the projections,
  3 players each.

## Ports

- `report/chapter-part.tsx` picks each part by the key of its chapter.
- The sim finale is not here. The app mounts the replay at the end of the last act.

## Does not do

- It computes no rate, no gap, and no projection. The pipeline writes them into the midseason file.
- It reads no file, no env, and no config (ADR 0012).
