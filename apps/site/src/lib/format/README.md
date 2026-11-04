# src/lib/format: the pure helpers of the pages over a league type

## Knows

- The stats-through segments of the as-of line, which the analyzer page and the trade finder share.
- The pure helpers over the rankings types, which a server component can call at build time.

## Ports

None.

## Does not do

- It reads no file, no storage, and no env. Each function takes values and returns values.
- It parses no published file. `src/lib/schemas/` holds the schemas, and `src/lib/data/` holds the loaders.
- It holds no plain number format. `packages/design/site/format/` holds those.
- It holds no format of the War chest page. `src/components/waiver/format.ts` holds those.
