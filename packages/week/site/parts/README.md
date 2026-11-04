# packages/week/site/parts: the parts of the league that the week and the other pages share

## Knows

- The avatar with the team name as one group, in `who.tsx`.
- The href of a manager page from the managers index href, in `hrefs.ts`. These builders need no base path.

## Ports

None.

## Does not do

- It holds no part with no league term. The design package holds those.
- It joins no base path. `apps/site/src/lib/routes.ts` builds each href with the base path.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
