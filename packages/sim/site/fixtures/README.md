# packages/sim/site/fixtures: the sim file fixture of the tests

## Knows

- `sim.json`, the season sim file in the exact shape the pipeline writes, from a real run of the sim of CPC 2026 week 8.
- `sim`, the same file parsed with the schema, so a stale fixture fails at import.
- `week-sim.json`, the week sim file in the exact shape the pipeline writes, from the sim step of CPC 2026 week 10.
- `week-sim-norcal.json`, the week sim file of NorCal 2026 week 10, a league with no median game.
- `weekSim` and `norcalWeekSim`, the two week files parsed with the schema.

## Ports

None.

## Does not do

- It serves no page. Only the tests import it.
- It is no published file. `make midseason-publish` publishes the sim file of a client with its report.
