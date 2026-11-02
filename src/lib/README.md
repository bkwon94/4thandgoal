# src/lib: the build config, the routes, the API client, and the browser stores

## Knows

- The build config in `src/lib/config.ts`, the route builders in `src/lib/routes.ts`, and the client of the site API in `src/lib/api.ts`.
- The types of each published file and of each API document, in the `src/lib/*-types.ts` files.
- The browser stores: the passphrase, the team pick of the War chest page, the teams list, and the theme.
- The motion timings, the default avatar and headshot, the usage helpers, and the `cn` helper.

## Ports

- The site API, through the client in `src/lib/api.ts`.
- The env, through `src/lib/config.ts`. No other module reads `process.env`.
- Local storage and session storage, through `src/lib/passphrase.ts`, `src/lib/team-pick.ts`, `src/lib/teams-store.ts`, and `src/lib/theme.ts`.
- GoatCounter, through `src/lib/usage.ts`.
- The headshots of the Sleeper CDN, through the URL in `src/lib/headshot.ts`.

## Does not do

- It holds no component and returns no markup. Components live in `src/components/`.
- It reads no published file. `src/lib/data/` holds the loaders.
- It holds no schema. `src/lib/schemas/` holds the Zod schemas. The types of a published file come from its schema.
- It infers no request type and no view type. We write those types by hand.
- It holds no React hook. Hooks live in `src/hooks/`.
