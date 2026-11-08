# packages/analyzer/site/form: the trade analyzer and the trade finder

## Knows

- The analyzer page body: the passphrase dialog, the trade form, and the result.
- The trade form, the Stack: the hero with its drift scene, the teams row, a card for each side, the sheets, the grade bar, the fold line, the sweep, and the error box.
- The result of one analyze document: the verdict hero with the decision, the fairness line, and the scene of one group per side (`analyzer-scene.ts`), the swap card, and a short text for each side.
- The trade finder, with up to three trades that are good for both, and the teams prefetch of the home page.
- `useRequest`, the guard of a call from a part to the API: the run id, the abort controller, and the unmounted flag.

## Ports

- The site API, through the client in `../lib/api.ts`. The calls are teams, analyze, and find, at `/clients/<slug>/`.
- The passphrase in local storage, through `../lib/passphrase.ts`.
- The teams list in session storage, through `../lib/teams-store.ts`.
- GoatCounter events, through `packages/design/site/lib/usage.ts`.
- Player headshots from the Sleeper CDN. The URL comes in the teams answer of the site API.

## Does not do

- It grades no trade. The site API grades it, and this folder shows the answer.
- It shows no roster grade. The roster grade lives in the managers part of the site.
- It defines no API shape. `../lib/schemas/api.ts` holds the response schemas.
- It reads no file, no env, and no config, and it imports no app. The page gives the API target and the finder flag.
