# packages/managers/site/page: the manager page and the managers index

## Knows

- The managers index and its Index list: a ledger of the teams in power-ranking order, filtered by the race chips All, In, Bubble, and Out. A row opens in place with the Open card, one at a time.
- The hero of a manager page in the hero slots, with the grade as the big number, the tiles Playoff, Bye, and Seed, and a W or L chip for each week. Its scene has one light per played week, bright for a win and dim for a loss, against the median of each week.
- The five chapters under the hero: Roster, Season So Far, Moves, Best Adds, and Top Performers. The Moves tiles are Trend tiles.
- The slot ranks, the points line, the bench points, and the season numbers.
- The Grade dial: four arcs, one for each part of the roster grade, each lit by its rank. Season So Far shows it under the letter and the read, and an open row of the Index list shows it small, in one row of four.
- The weight of each part of the grade, a copy of `GRADE_WEIGHTS` of the pipeline that a test compares to the tunables file.
- A league with no median game: the points line has no median line and no median key, and the season numbers have no record against the median.

## Ports

- Player headshots from the Sleeper CDN, through the URL from `@cpc/league/images`.
- The odds, the status word, and the power rank of each entry, which the site app joins from the rankings file.

## Does not do

- It computes no roster grade, no playoff odds, and no slot rank. The pipeline writes them into the managers file and the rankings file.
- It joins no files. `apps/site/src/lib/data/manager-data.ts` joins the managers file with the rankings file.
- It imports no other core package. The manager hrefs come from `@cpc/league/hrefs`.
- It builds no route. The app layer passes the managers index href (ADR 0012).
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
