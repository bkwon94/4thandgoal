# src/lib/schemas: the Zod schemas of the published files and the site API

## Knows

- One Zod schema per published file: the week page file, the rankings file, the managers file, and `waiver.json`.
- The schemas of the site API responses for the teams, analyze, and find calls.
- The keys that an older build may leave out, so the site reads every file the pipeline wrote.

## Ports

None.

## Does not do

- It owns no shape. The pydantic models of the pipeline own each shape, and a schema here follows them (ADR 0005).
- It holds no generated schema. We write each one by hand, and the test over the real files is the contract.
- It reads no file. `src/lib/data/` reads `public/` and parses each file with a schema here.
- It holds no type. The types of a published file in `src/lib/*-types.ts` come from a schema here.
- It holds no request type and no view type. We write those types by hand in `src/lib/`.
