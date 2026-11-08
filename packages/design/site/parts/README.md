# packages/design/site/parts: the parts that the pages share

## Knows

- The chapter, the label, the tag, and the blurb.
- The page column and the chapter rail.
- The team name.
- The one reveal of the site, the week line of a page with no hero, and the error line.
- The parts of the look (ADR 0024): the hero with its grid, glow, brackets, and six hero slots, and no free content; the card; the tile; the
  round photo frame with its initials; and the rise, the staggered entry of a page. Hero text sits on a `plate`.
- The data shape of the hero scene and its pure math, with no canvas, in `scene-math.ts` (ADR 0027).

## Ports

None.

## Does not do

- It holds no primitive. The shadcn primitives live in `site/ui/`.
- It holds no shell. The top band, the dock, and the theme button live in `site/shell/`.
- It holds no photo. The page passes the src of each avatar and headshot to the photo frame.
- Most parts serve two or more pages. `tag.tsx` and `error-line.tsx` serve one page today.
- It builds no route. The page passes each href, and a part only shows it (ADR 0012).
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
