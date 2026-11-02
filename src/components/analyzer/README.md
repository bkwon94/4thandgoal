# components/analyzer: the trade analyzer and the trade finder

## Knows

- The analyzer page body: the passphrase dialog, the trade form, and the result.
- The trade form: one group of pickers per side, and the destination of each player.
- The result of one analyze document: the decision for the asker, the fairness line, the swap card, and a read per side.
- The trade finder, with up to three trades that are good for both.

## Ports

- The site API, through the client in `lib/api.ts`. The calls are teams, analyze, and find.
- The passphrase in local storage, through `lib/passphrase.ts`.
- The teams list in session storage, through `lib/teams-store.ts`.
- GoatCounter events, through `lib/usage.ts`.

## Does not do

- It grades no trade. The site API grades it, and this folder shows the answer.
- It shows no letter grade. The roster grade lives in `components/managers/`.
- It defines no API shape. `lib/schemas/api.ts` holds the response schemas.
- It reads no file, no env, and no config, and it calls no loader (ADR 0004).
