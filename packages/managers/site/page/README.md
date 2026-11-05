# packages/managers/site/page: the manager page and the managers index

## Knows

- The managers index: one card per team in standings order, with the power rank, the playoff odds, the grade box, and the grade text.
- The hero of a manager page, with the grade as the big number, the tiles Playoff, Bye, and Seed, and a W or L chip for each week.
- The five chapters under the hero: Roster, Season So Far, Moves, Best Adds, and Top Performers.
- The slot ranks, the points line, the bench points, and the season numbers.
- A league with no median game: the points line has no median line and no median key, and the season numbers have no record against the median.

## Ports

- Player headshots from the Sleeper CDN, through the URL from `@cpc/league/images`.
- The odds and the power rank of each entry, which the site app joins from the rankings file.

## Does not do

- It computes no roster grade, no playoff odds, and no slot rank. The pipeline writes them into the managers file and the rankings file.
- It joins no files. `apps/site/src/lib/data/manager-data.ts` joins the managers file with the rankings file.
- It imports no other core package. The manager hrefs come from `@cpc/league/hrefs`.
- It builds no route. The app layer passes the managers index href (ADR 0012).
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
