# packages/eggs/site/lib: the client of the eggs routes and the passphrase store

## Knows

- The client of the eggs routes in `api.ts`, the Zod schema of each answer, and the port `EggsApi` that the parts call.
- The passphrase in local storage, under the same key as the trade analyzer.
- The board fixture in `fixtures/board.json`, which the API tests hold to the real answer, and the one fake of the port.

## Ports

- The eggs routes of the API, at `<url>/clients/<slug>/eggs/check`, `/claim`, and `/board`.
- Local storage, through `passphrase.ts`.

## Does not do

- It reads no env and no config. The app builds the target from its config.
- It owns no shape. The routes of the eggs package own each answer, and a schema here follows them.
