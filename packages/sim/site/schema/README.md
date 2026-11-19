# packages/sim/site/schema: the schema and the types of the sim file

## Knows

- The Zod schema of `sim.json`, the season sim file, in `sim.ts`.
- The Zod schema of `week-NN/sim.json`, the week sim file, and of its page block, in `sim.ts`. The page block has a playoff part with no regular week left.
- The Zod schema of the answer of the What-if route and of a set result, in `what-if.ts`.
- The types of the sim file and of the What-if in `sim-types.ts`. Each type comes from its schema.
- Only the parameters of the draw that the replay reads: the playoff spots, the byes, the median game, and the reseed.

## Ports

None.

## Does not do

- It owns no shape. `sim/published.py` of the Python side owns the shape, and the schema follows it (ADR 0013).
- It reads no file and makes no call. `apps/site/src/lib/data/sim-data.ts` reads `public/` and parses the file with this schema.
