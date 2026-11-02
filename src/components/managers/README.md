# components/managers: the manager page and the managers index

## Knows

- The managers index: one card per team in standings order, with the grade letter.
- The hero of a manager page, with the roster grade, the playoff odds, and the power rank.
- The five chapters under the hero: Roster, Season So Far, Moves, Best Adds, and Top Performers.
- The slot ranks, the points line, the bench points, and the season numbers.

## Ports

- Player headshots from the Sleeper CDN, through the URL from `lib/headshot.ts`.

## Does not do

- It computes no roster grade, no playoff odds, and no slot rank. The pipeline writes them into the managers file.
- It joins no files. `lib/data/manager-data.ts` joins the managers file with the rankings file.
- It builds no route. The app layer passes the managers index href (ADR 0004).
- It reads no file, no env, and no config, and it calls no loader (ADR 0004).
