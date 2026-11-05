# packages/week/site/fixtures: the week page fixture of the tests

## Knows

- The week 6 page of `clients/cpc/published/`, parsed with the schema, as `week6`.
- `firstSentence`, so a test finds a blurb on the page with no literal blurb text.

## Ports

None.

## Does not do

- It holds no made-up data. The tests read the real published file, so a change to its shape breaks them.
- It serves no page. Only the tests import it.
