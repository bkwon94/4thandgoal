# packages/sim/site/schema: the schema and the types of the sim file

## Knows

- The Zod schema of `sim.json`, the season sim file, in `sim.ts`.
- The types of the sim file in `sim-types.ts`. Each type comes from its schema.
- Only the parameters of the draw that the replay reads: the playoff spots, the byes, the median game, and the reseed.

## Ports

None.

## Does not do

- It owns no shape. `sim/published.py` of the Python side owns the shape, and the schema follows it (ADR 0013).
- It reads no file. `apps/site/src/lib/data/sim-data.ts` reads `public/` and parses the file with this schema.
