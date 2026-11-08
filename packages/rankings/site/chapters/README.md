# packages/rankings/site/chapters: the power rankings page, the Ladder, and the top three

## Knows

- The Ladder of the chosen week: the hero for the team at rank 1, a chip per week, one card for each other team, and the note on the four parts.
- The hero: "01", the team, the record, the movement, the tiles Playoff, Bye, and Seed, and the blurb.
- The hero keeps the static grid with no scene, because the Ladder under it already shows the race.
- The "Manager page" link of rank 1 in the action slot of the hero, because the Ladder starts at rank 2. With no
  managers href the hero shows no link.
- Each card: the rank, the avatar, the team, the record with the movement, and the playoff odds with a short bar. A tap opens the four part ranks, the blurb, and a link to the manager page.
- The chosen week, which the hero and the cards share. The URL hash carries it, such as `#week-5`.
- `RankingsScreen`, the whole page with its top band or its empty state.
- `TopThree`, the card of the home chapter: the top three, each with the rank, the avatar, the record with the movement, and the playoff odds, then a link to all teams.

## Ports

- The route and the home section of the app, in `apps/site/src/app/_routes/rankings/`, read the files and pass the data in.

## Does not do

- It computes no rank, no movement, and no playoff odds. The pipeline writes them into the rankings file.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012). The app layer passes the data of the rankings file.
- It imports no other core package. Its team row takes `Avatar` from `@cpc/league/avatar`, and the manager href comes from `@cpc/league/hrefs`.
