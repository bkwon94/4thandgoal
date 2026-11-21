# packages/analyzer/site/lib: the API client, the browser stores, and the API schemas

## Knows

- The client of the site API in `api.ts`. `ApiTarget` names the base URL, the client slug, and the season of each call.
- The Zod schemas of the teams, analyze, and find answers in `schemas/`, and the types from them in `analyze-types.ts`.
- The browser stores: the passphrase, the teams list, and the team pick of the War chest page.
- The trade of the Stack in `trade.ts`: each side, the players it gets with their source side, the body of `POST /analyze` that the picks build, and the level of the Ready halo.
- The stage lines in `stage-lines.ts`: the 12 lines that one trade on the stage gives, from one pure function.
- The clock of Deadline week in `deadline.ts`: the phase (open, last hours, closed, ended) and the countdown text from the time and the Lock, from one pure function.
- The favored side of a grade in `favored-side.ts`, from the Lean, which the mesh of the reveal dips toward.
- The mode of the analyzer from the query of its link, `?mode=grade` or `?mode=find`, in `mode.ts`. Find needs the finder flag.
- The stats-through segments of the as-of line, which the result and the trade finder share.
- The API fixtures of the tests in `fixtures/`, in the exact shape the site API returns.

## Ports

- The site API, at `<url>/clients/<slug>/teams`, `/analyze`, and `/find`. Local storage and session storage, through `passphrase.ts` and `teams-store.ts`.

## Does not do

- It reads no env and no config, and it imports no app. The app builds the target from its config.
- It owns no shape. The pydantic models of the analyzer own each answer, and a schema here follows them (ADR 0013). It holds no component and returns no markup. `../form/` holds the parts.
