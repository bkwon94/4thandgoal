# packages/rankings/site/chapters: the power rankings page, the table, and the top three

## Knows

- The power rankings table: one row per team for the chosen week, in rank order, and a chip per week.
- Each row: the rank, the movement, the team, the record, the playoff odds, and the four component ranks.
- The chosen week, which the masthead week line and the table share. The URL hash carries it, such as `#week-5`.
- `RankingsScreen`, the whole page with its masthead or its empty state, and `TopThree`, the row of the home chapter.

## Ports

- The route and the home section of the app, in `apps/site/src/app/_routes/rankings/`, read the files and pass the data in.

## Does not do

- It computes no rank, no movement, and no playoff odds. The pipeline writes them into the rankings file.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012). The app layer passes the data of the rankings file.
- It imports no other core package. Its team group and its manager href keep the markup and the path of the week parts.
