# packages/eggs/site/board: the egg board

## Knows

- The plain egg board in `egg-board.tsx`: the counts, each manager in each egg word with the letters, and the latest claims.
- The screen in `egg-board-screen.tsx`, which reads the board from the API at each visit.

## Ports

- `EggsApi` of `../lib/api.ts`. The app gives the real client, and a test gives the one fake.

## Does not do

- It shows no page, no spot, and no block.
