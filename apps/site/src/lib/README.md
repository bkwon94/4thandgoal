# src/lib: the build config, the routes, the loaders, and the client values

## Knows

- The build config in `src/lib/config.ts`, with the API target of the analyzer, and the route builders in `src/lib/routes.ts`.
- The types of the client values in `src/lib/client-values.ts`. Each package holds the schema and the types of its own published file.
- The default avatar and headshot are in `@cpc/league`.

## Ports

- The env, through `src/lib/config.ts`. No other module reads `process.env`.

## Does not do

- It holds no component and returns no markup. Each package holds its own components.
- It reads no published file. `src/lib/data/` holds the loaders.
- It holds no schema of a published file. Each package holds the Zod schema of its own file, in `packages/<package>/site/`.
- It infers no request type and no view type. We write those types by hand.
- It holds no API client, no browser store, and no React hook. `@cpc/analyzer` holds the API client, the stores, and `useRequest`.
- It holds no theme, no motion timing, no usage count, and no `cn` helper. The design package holds them.
