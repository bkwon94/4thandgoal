# src/components/parts: the parts that the pages share

## Knows

- The chapter, the label, the tag, and the blurb.
- The page column and the chapter rail.
- The team avatar, the player headshot, the team name, and the avatar with the name as one group.
- The one reveal of the site, the week line of the masthead, and the error line.

## Ports

None.

## Does not do

- It holds no primitive. The shadcn primitives live in `src/components/ui/`.
- It holds no shell. The masthead, the menu, and the theme button live in `src/components/shell/`.
- Most parts serve two or more pages. `tag.tsx` and `error-line.tsx` serve one page today.
- It builds no route. The page passes each href, and a part only shows it (ADR 0012).
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
