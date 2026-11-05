# packages/design/site/shell: the shell of every page

## Knows

- The top band: the brand mark, the pill bar, the week chip, and the theme button. It is sticky, so it stays on screen at every scroll.
- The pill bar: each destination with its full label, from the desktop tier up. The dock: each destination as an icon and a short label, fixed at the bottom of a phone and a tablet.
- The week chip, "WK 08", and the strip of the weeks of the season that it opens. The chip week has the brand edge.
- The open destination: `currentHref` in `nav.ts` marks the item of the open page, a page under it, or any week.
- The theme button. Every brand has both sets, so every top band shows it.
- The count script tag of the head.

## Ports

- The theme choice in local storage, through `site/lib/theme.ts`.
- GoatCounter events and the count script, through `site/lib/usage.ts`.

## Does not do

- It builds no menu link and lists no week. `apps/site/src/app/shell-props.ts` builds the destinations and the weeks.
- It takes no layout from a client. The look owns the navigation (ADR 0024).
- It sets no theme before the first paint. The root layout inlines the boot script from `site/lib/theme.ts`.
- It holds no chapter and no hero. Each page folder holds its chapters, and the hero lives in `site/parts/`.
- It holds no primitive. The primitives live in `site/ui/`, and the strip of weeks is a native `details` element.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
