# packages/midseason/site/fixtures: the midseason file fixture of the tests

## Knows

- `midseason.json`, the season file in the exact shape the pipeline writes, from a real build of CPC 2026 week 8.
- `midseason`, the same file parsed with the schema, so a stale fixture fails at import.

## Ports

None.

## Does not do

- It serves no page. Only the tests import it.
- It is no published file. `make midseason-publish` publishes the report of a client.
