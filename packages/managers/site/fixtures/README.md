# packages/managers/site/fixtures: the managers file fixture of the tests

## Knows

- The managers file in the exact shape that the pipeline writes, parsed with the schema, as `managers`.

## Ports

None.

## Does not do

- It holds no made-up shape. A change to the shape of the file breaks the parse at import, so a stale fixture fails at once.
- It serves no page. Only the tests import it.
