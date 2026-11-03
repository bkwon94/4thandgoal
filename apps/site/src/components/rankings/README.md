# src/components/rankings: the power rankings table

## Knows

- The power rankings table: one row per team for the chosen week, in rank order, and a chip per week.
- Each row: the rank, the movement, the team, the record, the playoff odds, and the four component ranks.
- The chosen week, which the masthead week line and the table share. The URL hash carries it, such as `#week-5`.

## Ports

None.

## Does not do

- It computes no rank, no movement, and no playoff odds. The pipeline writes them into the rankings file.
- It holds the helpers that turn one row into markup. The pure rankings helpers live in `src/lib/format/rankings.ts`.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012). The app layer passes the data of the rankings file.
