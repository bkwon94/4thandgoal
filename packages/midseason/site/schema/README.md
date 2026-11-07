# packages/midseason/site/schema: the schema and the types of the midseason file

## Knows

- The Zod schema of `midseason.json`, the season file of the midseason report, in `midseason.ts`.
- The types of the midseason file in `midseason-types.ts`. Each type comes from its schema.
- The full facts of the opener and of each chapter that the page renders. A chapter with no part keeps its facts unknown.

## Ports

None.

## Does not do

- It owns no shape. `midseason/published.py` of the pipeline side owns the shape, and the schema follows it (ADR 0013).
- It reads no file. `apps/site/src/lib/data/midseason-data.ts` reads `public/` and parses the file with this schema.
