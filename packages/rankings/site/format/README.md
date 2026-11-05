# packages/rankings/site/format: the pure helpers over the rankings types

## Knows

- `biggestMover`, the team with the largest movement of one week, for the home chapter.

## Ports

None.

## Does not do

- It reads no file, no storage, and no env. Each function takes values and returns values.
- It holds no plain number format. `packages/design/site/format/` holds those.
