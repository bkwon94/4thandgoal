# lib/format: the pure formats and helpers of the pages

## Knows

- The number and name formats of the week page, ported from the Jinja filters of the pipeline.
- The stats-through segments of the as-of line, which the analyze page and the trade finder share.
- The pure helpers over the rankings types, which a server component can call at build time.

## Ports

None.

## Does not do

- It reads no file, no storage, and no env. Each function takes values and returns values.
- It parses no published file. `lib/schemas/` holds the schemas, and `lib/data/` holds the loaders.
- It is not a client module, so it holds no React hook and no state.
- It holds no format of the waiver page. `components/waiver/format.ts` holds those.
