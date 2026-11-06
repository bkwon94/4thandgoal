# packages/sim/site/fixtures: the sim file fixture of the tests

## Knows

- `sim.json`, the season sim file in the exact shape the pipeline writes, from a real run of the sim of CPC 2026 week 8.
- `sim`, the same file parsed with the schema, so a stale fixture fails at import.

## Ports

None.

## Does not do

- It serves no page. Only the tests import it.
- It is no published file. `make midseason-publish` publishes the sim file of a client with its report.
