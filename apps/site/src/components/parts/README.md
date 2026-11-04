# src/components/parts: the parts of the league that the pages share

## Knows

- The avatar with the team name as one group. The team avatar and the player headshot are in `@cpc/league`.

## Ports

None.

## Does not do

- It holds no part with no league term. The design package holds those in `packages/design/site/parts/`.
- It holds no primitive and no shell. The design package holds them in `site/ui/` and `site/shell/`.
- It builds no route. The page passes each href, and a part only shows it (ADR 0012).
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
