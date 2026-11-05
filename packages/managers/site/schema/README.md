# packages/managers/site/schema: the schema and the types of the managers file

## Knows

- The Zod schema of `managers.json`, the season managers file, in `managers.ts`.
- The types of the managers file in `manager-types.ts`. Each type comes from its schema.
- The joined `Manager` and `Managers` types, which the loader of the site app builds.
- The median of a week is null for a league with no median game.

## Ports

- `JoinedOdds`: the playoff percent that the site app joins from the rankings file.

## Does not do

- It owns no shape. The pydantic models of the managers package own the shape, and the schema follows them (ADR 0013).
- It reads no file. `apps/site/src/lib/data/manager-data.ts` reads `public/` and parses the file with this schema.
- It imports no rankings type, so the managers package stands alone.
