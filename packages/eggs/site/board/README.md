# packages/eggs/site/board: the egg board, the egg button, and the egg banner

## Knows

- The egg board in `egg-board.tsx`, from the top: the hero with the counts left to find, found, and to drop over the grid of the 54 eggs, one card per egg word with its gift card, its leader, the top 5, and "Show all 11", the latest claims, and how the hunt works. A won egg word is a hero card with a WON stamp and its winner.
- The screen in `egg-board-screen.tsx`, which reads the board from the API at each visit.
- The egg button in `egg-button.tsx`: a link to the egg board for the top band, with a red badge of the count left to find.
- The egg banner in `egg-banner.tsx`: the strip under the top band of the home page. It names the day of the last drop, such as "6 eggs dropped today · 6 left", then "6 eggs dropped Tue · 5 left". A hide stays in this browser until the next drop.
- `use-board.ts`: the board for the button and the banner, which show nothing of the board while it loads or when the call fails.

## Ports

- `EggsApi` of `../lib/api.ts`. The app gives the real client, and a test gives the one fake.
- Local storage, through `../lib/banner-store.ts`, for the hide state of the banner.

## Does not do

- It shows no page, no spot, and no block.
- It builds no href. The app passes the href of the egg board.
- It mounts nothing in the top band or on the home page. The registry of the client build mounts the button and the banner for a client of the eggs package.
