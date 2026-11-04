# packages/rankings/site/schema: the schema and the types of the rankings file

## Knows

- The Zod schema of `rankings.json`, the season file of the rankings, in `rankings.ts`.
- The types of the rankings file in `rankings-types.ts`. Each type comes from its schema.
- The odds of a row. The managers pages take the `Odds` type from here.

## Ports

None.

## Does not do

- It owns no shape. `rankings/published.py` of the pipeline side owns the shape, and the schema follows it (ADR 0013).
- It reads no file. `apps/site/src/lib/data/rankings-data.ts` reads `public/` and parses the file with this schema.
