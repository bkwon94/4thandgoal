# packages/sim/site/page: the sim page of Your team

## Knows

- `SimPage`: layout D "Cards" of decision 04. The header shows the avatar, the name, the record, the weeks left, and the playoff odds. The sentence of more wins, as the build writes it, opens the ladder sheet: each count of more wins, its odds, and its chance.
- The week switch: each regular week left, then Playoffs. A week page holds the week card, with one tile per result of Your team, four with the median game and two with none, and the root-for card. On a phone the root-for card opens from one row. From the tablet tier it always shows.
- A number with the "about" flag of the file reads "about X%" (`format.ts`). `TeamPick`: the pick of a team for a visitor with no team kept.
- The What-if in `use-what-if.ts`. A tap on a tile sets that result, and a tap on the set tile clears it. The next week opens 400 ms after a set. Each tap calls the What-if port at once and cancels the call before it.
- The header odds, the sentence, the ladder, the weeks, and the Playoffs page take the page of the answer. A set week keeps its tiles and its root-for card as they were at the tap, so the tiles still show the odds of each other result.
- The set line lists each set result, with a Reset back to the numbers of the file. A failed call goes back to the set results of the last answer, and one line says "The What-if is not available now."
- With no regular week left, the page reads the playoff part of the page block (`in-playoffs.tsx`): the title odds in the header, no week switch, and no ladder. A team still in sees its game of the round with two tiles, the title odds after a win and after a loss, which set a What-if as the tiles of a week do. A team on a bye sees its bye, with no tile.
- A team out of the playoffs sees "Out of the playoffs". Each playoff page shows the title odds of each team left and the bracket. After the final, the page shows the champion and the final bracket, with no tile and no sim button.
- "Sim week N" and "Sim the season" sit in the flow under the week page, and open the replay of `stage/`. The Playoffs page and the playoff weeks before the final have only "Sim the season". While a call runs, both wait, so the replay plays a run of the set line.

## Ports

- The props of `SimPage`: the parsed week sim file, the roster id of Your team, the avatars, and the What-if port of `lib/what-if-api.ts`.

## Does not do

- It draws no score and runs no sim. Each number comes from the page block of `sim.json` or of a What-if answer.
- It makes no call with no set result, and no call of its own. The port of the app makes the call.
- It has no grid of every game and no chart of the odds by week. The only result tiles are those of Your team, and a bracket game whose two teams are not set has no tile.
- It reads no file, no env, no config, and no storage (ADR 0012). The app reads Your team.
