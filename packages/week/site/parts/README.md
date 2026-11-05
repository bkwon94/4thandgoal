# packages/week/site/parts: the parts of the league that the week and the other pages share

## Knows

- The avatar with the team name as one group, in `who.tsx`.

## Ports

None.

## Does not do

- It holds no part with no league term. The design package holds those.
- It builds no manager href. `@cpc/league/hrefs` holds the builders, because the week and the managers both link a manager page.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
