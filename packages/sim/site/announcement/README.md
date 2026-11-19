# packages/sim/site/announcement: the art of the sim Announcement

## Knows

- `previewOf`: the few numbers of `week-NN/sim.json` that the art needs. They are the standings in the order of the sim, the playoff spots, the median game, and the What-if odds of each team.
- `SimPreview`: Your team's name and playoff odds, three standings rows around Your team with the playoff line, and the What-if chip.
- The chip is a button. A tap turns it on or off, and the odds count to the new number. It turns on once by itself, `AUTO_WHAT_IF_MS` after the sheet stops, unless the manager tapped it first.
- The What-if of the chip: Your team wins its game of the next week. With the median game it also beats the median, and the chip reads "win both".
- Under reduced motion the rows and the odds show at once, and the chip does not turn on by itself.

## Ports

- The props of `SimPreview`: the data of `previewOf`, the roster id of Your team, and `settled`, which the Announcement sets once the sheet stops.

## Does not do

- It holds no sheet, no copy, and no rule of when the Announcement opens. The general Announcement is in `packages/design/site/parts/announcement.tsx`, and the app holds the rules.
- It runs no sim and makes no call to the API. Each number comes from the week sim file.
- It reads no file, no env, no config, and no storage (ADR 0012). The app reads Your team.
