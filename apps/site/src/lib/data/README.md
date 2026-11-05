# src/lib/data: the loaders of the published files

## Knows

- One loader per published file: the week page file, the rankings file, the managers file, and `waiver.json`.
- Where each file sits under `public/`, and which week folders hold `waiver.json`.
- The join of the managers file with the last week of the rankings file.
- Whether the waiver route and the managers route are on. `next.config.ts` builds each one only when its file exists.
- The test of every published file against its schema, in `src/lib/data/published-files.test.ts`.

## Ports

- The reads of `public/` with `node:fs`, at build time only.

## Does not do

- It owns no shape. The pipeline owns each shape, and each package holds the schema of its own file (ADR 0013).
- It runs in no browser. Only the app layer and `next.config.ts` call a loader (ADR 0012).
- It writes no file. The pipeline publishes every file under `public/`.
- It formats no number. Each package holds its own formats.
