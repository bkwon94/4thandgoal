# packages/week/site/schema: the schema and the types of the week page file

## Knows

- The Zod schema of `page.json`, the week page file, in `week.ts`.
- The types of the week page file in `week-types.ts`. Each type comes from its schema.
- The team, the avatar map, and the headshot map. The other packages take these types from here.

## Ports

None.

## Does not do

- It owns no shape. The pydantic models of the pipeline own the shape, and the schema follows them (ADR 0013).
- It reads no file. `apps/site/src/lib/data/week-data.ts` reads `public/` and parses each file with this schema.
