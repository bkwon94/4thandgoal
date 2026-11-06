# packages/sim/site/replay: the replay of one stored sim run

## Knows

- `SimReplay`: each press plays one random run of the stored runs, beside the odds of all runs.
- The season of a run in `season.ts`: the standings after each week, the seeds, the bracket, and the champion.
- The beats of the Broadcast motion and their holds in `beats.ts` (decision 13 of `midseason-report`).
- The parts of the stage: the week strip, the standings, the lower third, the bracket, and the champion card.
- The pace in `pace.ts`: full motion, a fade only under reduced motion, and a skip that shows each part at rest.

## Ports

- The props of `SimReplay`: the parsed sim file, and a pick of the run that a test may pass.

## Does not do

- It draws no score. Each score comes from the stored run.
- It has no control to pick the winner of a game (decision 08 of `midseason-report`).
- It imports nothing of the midseason report. The app mounts it as the finale of the report.
- It reads no file, no env, and no config (ADR 0012).
