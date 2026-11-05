# packages/rankings/site/fixtures: the rankings file fixture of the tests

## Knows

- `rankings.json`, the season file in the exact shape the pipeline writes, with the week 6 teams and records.
- `rankings`, the same file parsed with the schema, so a stale fixture fails at import.

## Ports

None.

## Does not do

- It serves no page. Only the tests import it.
