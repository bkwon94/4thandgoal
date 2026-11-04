# packages/week/site/chapters: the chapters of the weekly report

## Knows

- The game changer, the awards, the matchup of the week, the median game, and the standings.
- All matchups with the recap of each game, the position leaders, the trades, and next week with its byes.
- The week footer, with a link to the prior week and the next week.

## Ports

None.

## Does not do

- It computes no score, no award, and no blurb. The pipeline writes them into the week page file.
- It finds no prior week or next week. The app layer finds both at build time.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012). `apps/site/src/lib/data/week-data.ts` reads the week page file.
- It imports no app. The page passes each href and the managers index href as props (ADR 0023).
