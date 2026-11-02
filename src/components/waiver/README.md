# components/waiver: the War chest waiver page

## Knows

- The War chest page: the budget ring, the bucket tabs, the drift field, the open player, and the rest of the bucket.
- The drift field: the top six of the open bucket, each in a fixed slot of the layout table.
- The team pick, with the team and its budget. It uses the team picker of `components/analyzer/`.
- The text formats of the page: the price, the trending line, the stance, and the drop line.

## Ports

- The team pick in local storage, through `lib/team-pick.ts`.
- Player headshots from the Sleeper CDN, through the URL from `lib/headshot.ts`.

## Does not do

- It sets no price and no bid, and it does no research. The pipeline writes them into `waiver.json`.
- It calls no API.
- It reads no file, no env, and no config, and it calls no loader (ADR 0004). `lib/data/waiver-data.ts` reads `waiver.json`.
