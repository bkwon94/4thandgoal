# packages/sim/site/announcement: the art of The Race Announcement

## Knows

- `previewOf`: the few numbers of `week-NN/sim.json` that the art needs. They are the rows of the League board for a playoff spot, in odds order, each with its name, record, odds, and pill.
- `SimPreview`: Your team's name and odds of a playoff spot, and three League board rows around Your team. Your team's row has the "You" tag and the accent bar.
- The pill names the best Goal locked, "Clinched 1 seed", "Clinched bye", or "Clinched spot", or reads "Out". A team in the hunt shows no pill, as on the League board.
- The rows rise in with a stagger, the bars fill, and the odds of Your team count up. Under reduced motion each part shows at once.

## Ports

- The props of `SimPreview`: the data of `previewOf` and the roster id of Your team.

## Does not do

- It holds no sheet, no copy, and no rule of when the Announcement opens. The general Announcement is in `packages/design/site/parts/announcement.tsx`, and the app holds the rules.
- It has no control. A tap on the art does nothing; the link of the sheet opens The Race.
- It runs no sim and makes no call to the API. Each number comes from the week sim file.
- It reads no file, no env, no config, and no storage (ADR 0012). The app reads Your team.
