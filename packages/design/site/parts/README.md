# packages/design/site/parts: the parts that the pages share

## Knows

- The chapter, the label, the tag, the blurb, and the team name.
- The page column, which a wide page widens to the top band from the desktop tier, and the chapter rail.
- The one reveal of the site, the week line of a page with no hero, and the error line.
- The Announcement, the bottom sheet on the shared Sheet that introduces one new feature: an art slot, an eyebrow, a title, one line, the link, and "Not now". The use fills the art and the copy, and passes the site name.
- The Open card, the one part that opens and closes a card in place (ADR 0028). Its row look has no frame and no chevron, for a row of a ledger.
- The parts of the look (ADR 0024): the hero with its grid, glow, brackets, and seven hero slots, and no free content; the hero frame, which takes free content for the parts of the egg hunt only; the card; the tile, and the Trend tile with its bars, stepped area, or dots of a week series; the
  round photo frame with its initials; and the rise, the staggered entry of a page. Hero text has no plate (ADR 0036).
- The hero scene (ADR 0027): the math in `scene-math.ts` and `scene-motion.ts`, the canvas, and the drift in `drift-scene.ts`, which the 404 uses. The mesh, the live grid art that a page passes to a hero as its `art`: the math in `mesh-math.ts` and the runner in `mesh-canvas.ts`. The runner draws the idle mesh, and with `waitDrive` a weight under each `[data-mesh-anchor]` in turn and the light pulses of the grade wait. With `revealDrive`, the lines in the box of the favored anchor flash once, and the mesh dips toward it and goes flat. The flash and the light of the dip stay in that box, because the rows of the stage stack one row apart.

## Ports

The browser storage: `scene-canvas.ts` reads and writes `window.localStorage` for the hint flag.

## Does not do

- It holds no primitive. The shadcn primitives live in `site/ui/`.
- It holds no shell or photo. The top band, the menu sheet, and the theme button live in `site/shell/`, and the page passes the src of each avatar and headshot to the photo frame.
- Most parts serve two or more pages. `tag.tsx` and `error-line.tsx` serve one page today.
- It builds no route. The page passes each href, and a part only shows it (ADR 0012).
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
