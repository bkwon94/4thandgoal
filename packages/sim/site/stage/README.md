# packages/sim/site/stage: the replay of the sim page

## Knows

- `SimStage`: three screens on one stage that never scrolls, Season, Playoffs, and Champion, for "Sim the season" (decision 04).
- "Sim week N" plays two parts in turn, Games, then Standings. The games show Your game first and one median line.
- The Season screen shows the standings in the Race style: the byes fold into one line, places past three below the playoff line fold into one line, and Your team never folds.
- The Playoffs screen plays one round at a time. The Champion screen says where Your team finished.
- The stage opens as a fixed layer under the site header. It has a header row with the tabs and the close, a body, and the controls in their own row.
- A tab of a screen that has played goes back to it. A tab of a screen not yet played is off.
- The pick in `pick.ts`: a stored run comes up with a chance in proportion to its weight, so the replay of a What-if follows its set results.
- The timeline in `steps.ts`: each step and its hold.
- Under reduced motion, each change is a fade. No part moves.

## Ports

- The props of `SimStage`: the week sim file, the stored runs with their weights, the avatars, Your team, the ask, the random number, and the close.

## Does not do

- It draws no score. Each score comes from a stored run.
- It changes nothing of `replay/`, the replay of the midseason report. It reads only `replay/season.ts`.
- It reads no file, no env, no config, and no storage (ADR 0012).
