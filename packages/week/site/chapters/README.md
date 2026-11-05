# packages/week/site/chapters: the chapters of the weekly report

## Knows

- The hero of the week page: the matchup of the week. It stays dark in light.
- The four numbers under the hero: the top score, the median, the closest margin, and the Game Changer gap.
- Every game, with the recap of each game behind a tap, the Game Changer, the awards, and the position leaders.
- The trades, the median game, the standings, and next week with its byes.
- The week footer, with a link to the prior week and the next week.
- The hero of the home page: the matchup of the latest week with its margin, both teams, the first sentence of the blurb, and a "Read Week N" button.

## Ports

None.

## Does not do

- It computes no score, no award, and no blurb. The pipeline writes them into the week page file.
- It finds no prior week or next week. The app layer finds both at build time.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012). `apps/site/src/lib/data/week-data.ts` reads the week page file.
- It imports no app. The page passes each href and the managers index href as props (ADR 0023).
