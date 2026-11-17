# packages/analyzer/site/form: the trade analyzer and the trade finder

## Knows

- The analyzer page body: the passphrase dialog, the trade form, and the result.
- The trade form, the Stack: the hero, the teams row, a card for each side, the sheets, the grade bar with its Ready halo, the sweep of the finder wait, the stage lines, the trade on the stage as one row per side with a count in idle and headshot tokens in the wait, and the error box.
- The result of one analyze document: the read hero with the trade on the stage, the Lean on its 5-step scale, the Case, the fairness line with each long reason folded under More, one tab per side with Edit in its header, and the Bullet rows in `bullet-rows.tsx`, which the Finder card reuses. It arrives in a staged reveal of about 1 s over the mesh, or in one plain fade with motion off.
- The trade finder, with an optional partner and up to three picks of the Advisor, each with a headline, the swap card, and the Bullet rows. The swap card shows only in the Finder. After a fallback, each trade of the shortlist shows its fact lines. The teams prefetch of the home page.
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
