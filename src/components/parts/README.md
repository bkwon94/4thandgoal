# components/parts: the parts that every page shares

## Knows

- The chapter, the label, the tag, and the blurb.
- The page column and the chapter rail.
- The team avatar, the player headshot, the team name, and the avatar with the name as one group.
- The one reveal of the site, the week line of the masthead, and the error line.

## Ports

None.

## Does not do

- It holds no primitive. The shadcn primitives live in `components/ui/`.
- It holds no shell. The masthead, the menu, and the theme button live in `components/shell/`.
- It holds no component of one page only. That component lives in the folder of its page, such as `components/week/`.
- It builds no route. The page passes each href, and a part only shows it (ADR 0004).
- It reads no file, no env, and no config, and it calls no loader (ADR 0004).
