# src/components/waiver: the War chest page

## Knows

- The War chest page: the budget ring, the bucket tabs, the drift field, the open player, and the rest of the bucket.
- The drift field: the top six of the open bucket, each in a fixed slot of the layout table.
- The team pick, with the team and its budget. It uses the team picker of `src/components/analyzer/`.
- The text formats of the page: the price, the trending line, the stance, and the drop line.

## Ports

- The team pick in local storage, through `src/lib/team-pick.ts`.
- Player headshots from the Sleeper CDN, through the URL from `src/lib/headshot.ts`.

## Does not do

- It sets no price or bid, and it does no research. The pipeline writes the prices, the bids, and the research claims into `waiver.json`.
- It calls no API.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012). `src/lib/data/waiver-data.ts` reads `waiver.json`.
