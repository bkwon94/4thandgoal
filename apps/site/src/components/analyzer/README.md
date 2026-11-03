# src/components/analyzer: the trade analyzer and the trade finder

## Knows

- The analyzer page body: the passphrase dialog, the trade form, and the result.
- The trade form: one group of pickers per side, and the destination of each player.
- The result of one analyze document: the decision for the asker, the fairness line, the swap card, and a short text for each side.
- The trade finder, with up to three trades that are good for both.

## Ports

- The site API, through the client in `src/lib/api.ts`. The calls are teams, analyze, and find.
- The passphrase in local storage, through `src/lib/passphrase.ts`.
- The teams list in session storage, through `src/lib/teams-store.ts`.
- GoatCounter events, through `src/lib/usage.ts`.
- Player headshots from the Sleeper CDN. The URL comes in the teams answer of the site API.

## Does not do

- It grades no trade. The site API grades it, and this folder shows the answer.
- It shows no roster grade. The roster grade lives in `src/components/managers/`.
- It defines no API shape. `src/lib/schemas/api.ts` holds the response schemas.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
