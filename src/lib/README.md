# lib: the build config, the routes, the API client, and the browser stores

## Knows

- The build config in `config.ts`, the route builders in `routes.ts`, and the client of the site API in `api.ts`.
- The types of each published file and of each API document, in the `*-types.ts` files.
- The browser stores: the passphrase, the team pick of the waiver page, the teams list, and the theme.
- The motion timings, the default avatar and headshot, the usage helpers, and the `cn` helper.

## Ports

- The site API, through the client in `api.ts`.
- The environment variables, through `config.ts`. No other module reads `process.env`.
- Local storage and session storage, through `passphrase.ts`, `team-pick.ts`, `teams-store.ts`, and `theme.ts`.
- GoatCounter, through `usage.ts`, and the Sleeper CDN headshot URL in `headshot.ts`.

## Does not do

- It holds no component and returns no markup. Components live in `src/components/`.
- It reads no published file. `lib/data/` holds the loaders.
- It holds no schema. `lib/schemas/` holds the Zod schemas, and each type here comes from one.
- It holds no React hook. Hooks live in `src/hooks/`.
