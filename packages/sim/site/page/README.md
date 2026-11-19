# packages/sim/site/page: the sim page of Your team

## Knows

- `SimPage`: layout D "Cards" of decision 04. The header shows the avatar, the name, the record, the weeks left, and the playoff odds.
- The sentence of more wins, as the build writes it, opens the ladder sheet: each count of more wins, its odds, and its chance.
- The week switch: each regular week left, then Playoffs. A week page holds the week card and the root-for card.
- The week card has one tile per result of Your team: four with the median game, two with none.
- On a phone the root-for card opens from one row. From the tablet tier it always shows.
- A number with the "about" flag of the file reads "about X%" (`format.ts`).
- `TeamPick`: the pick of a team for a visitor with no team kept.
- With no regular week left, the page reads the playoff part of the page block (`in-playoffs.tsx`). The header shows the title odds, and the page has no week switch and no ladder.
- In the playoffs, a team still in sees its game of the round with two tiles, the title odds after a win and after a loss. A team on a bye sees its bye, with no tile.
- A team out of the playoffs sees "Out of the playoffs". Each playoff page shows the title odds of each team left and the bracket.
- After the final, the page shows the champion and the final bracket, with no tile.

## Ports

- The props of `SimPage`: the parsed week sim file, the roster id of Your team, and the avatars.

## Does not do

- It draws no score and runs no sim. Each number comes from the page block of `sim.json`.
- It makes no call to the API.
- It has no grid of every game. The only result tiles are those of Your team.
- It offers no tile for a bracket game whose two teams are not set, and no chart of the odds by week.
- It reads no file, no env, no config, and no storage (ADR 0012). The app reads Your team.
