# packages/sim/site/page: the sim page of Your team

## Knows

- `SimPage` in the regular season is The Race, variant D of decision 04 of playoff-paths: the title, the Goal switch (`goal-switch.tsx`) that opens on the open Goal of the page block, and the Your team card in a `Collapsible`. Its head shows the avatar, the name, the record, and the odds of the Goal. Open, it holds the Finish list (`finish-list.tsx`), the week card (`week-card.tsx`), and the replay buttons. A tap on a Finish opens its Paths in place, with the copy of decision 06 of playoff-paths (`finish-copy.ts`). A tap on another team of the board opens its sheet (`team-sheet.tsx`) with its Finish list and "Make this Your team", which calls `onYou`.
- The League board (`league-board.tsx`): one bar per team in odds order for the Goal, a tie in the order of the standings. It uses the bar chart of `@cpc/design/ui/bar-chart`, with one tab stop and the arrow keys. Each bar is ink at 80%, and only Your team takes the accent and the "You" tag. A tap on Your team opens and shows its card. A quiet pill marks a team Clinched or Out of the Goal, naming the best Goal locked, and a team In the hunt has none. The Clinch lines of the spot or the bye sit under their team, with the copy of decision 06 of playoff-paths (`clinch-copy.ts`). A Seed Goal shows none. `goals.ts` holds the names of each Goal, the pill, and the order of the board. A file written before The Race gives only the spot, from the playoff odds.
- The week card of the next regular week: the Score to beat against the opponent and the median, "to win" and "to be sure", the tiebreak gap when it is close, one tile per result of Your team with the odds of the Goal after it, four with the median game and two with none, and the root-for list of the chosen result. The list holds every other game with both results and their odds, a gray "Doesn't matter" on a game under 1 point, and 1 or 2 median rows. Before a tap it shows the most likely result. A seed and a Goal that is not open show one line in place of the list.
- A number with the "about" flag reads "about X%" (`format.ts`). `TeamPick` picks a team for a visitor with none kept. The What-if in `use-what-if.ts`. A tap on a tile sets that result, and a tap on the set tile clears it. Each tap calls the What-if port at once and cancels the call before it.
- The header odds, the sentence, the Finish list, the week card, and the League board take the page and the board of the answer. The week card keeps its tiles as they were at the tap of its week, so each other tile still shows the odds of its result.
- The set line lists each set result, with a Reset back to the numbers of the file. A failed call goes back to the set results of the last answer, and one line says "The What-if is not available now."
- With no regular week left, the page reads the playoff part of the page block (`in-playoffs.tsx`): the title odds in the header, no week switch, and no ladder. A team still in sees its game of the round with two tiles, the title odds after a win and after a loss, which set a What-if as the tiles of a week do. A team on a bye sees its bye, with no tile.
- A team out of the playoffs sees "Out of the playoffs". Each playoff page shows the title odds of each team left and the bracket. After the final, the page shows the champion and the final bracket, with no tile and no sim button.
- "Sim week N" and "Sim the season" sit in the flow under the week card, and open the replay of `stage/`. The playoff weeks before the final have only "Sim the season". While a call runs, both wait, so the replay plays a run of the set line.

## Ports

- The props of `SimPage`: the parsed week sim file, the roster id of Your team, the avatars, the What-if port of `lib/what-if-api.ts`, and `onYou`, which the app calls to keep another team as Your team.

## Does not do

- It draws no score and runs no sim. Each number comes from the page block of `sim.json` or of a What-if answer.
- It makes no call with no set result, and no call of its own. The port of the app makes the call.
- It has no grid of every game and no chart of the odds by week. The only result tiles are those of Your team, and a bracket game whose two teams are not set has no tile.
- It reads no file, no env, no config, and no storage (ADR 0012). The app reads Your team.
