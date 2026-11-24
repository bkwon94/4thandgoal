# packages/sim/site/fixtures: the sim file fixture of the tests

## Knows

- `sim.json`, the season sim file in the exact shape the pipeline writes, from a real run of the sim of CPC 2026 week 8.
- `sim`, the same file parsed with the schema, so a stale fixture fails at import.
- `week-sim.json`, the week sim file in the exact shape the pipeline writes, from the sim step of CPC 2026 week 10.
- `week-sim-norcal.json`, the week sim file of NorCal 2026 week 10, a league with no median game. `weekSim`, `weekElevenSim`, and `norcalWeekSim` parse the three week files.
- `week-sim-week-11.json`, the week sim file of CPC 2026 week 11 from `make sim CLIENT=cpc WEEK=11`, with the Goals and the Finish lists of each page and the League board. Bo Girds is 11-11 with 3 weeks left.
- `what-if-win-above.json` and `what-if-loss-below.json`, two answers of the local What-if route on `week-sim.json`, with Bo Girds
  set to a win over the median and to a loss under it in week 11. `what-if-week-11-try-it.json`, the answer on `week-sim-week-11.json`
  for "Try it" on the plan of the first 4-2 Path of Bo Girds, built as the route builds it. The week 11 file keeps the published names.
- `fakeWhatIfApi`, the one fake of the What-if port over those three answers. It keeps each call and its signal.
- `week-sim-playoffs.json`, `week-sim-round-2.json`, and `week-sim-final.json`, the playoff fixtures of the season-sim acceptance tests. Each takes the inputs of CPC 2026 week 10 and plays the later weeks as stored run 1, then runs as week 14, 15, and 17. `make sim-fixtures` in `apps/pipeline` writes them.
- `playoffsWeekSim`, `roundTwoWeekSim`, and `finalWeekSim`, the three playoff fixtures parsed with the schema.

## Ports

None.

## Does not do

- It serves no page. Only the tests import it.
- It is no published file. `make midseason-publish` publishes the sim file of a client with its report.
