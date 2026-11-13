# packages/design/site/shell: the shell of every page

## Knows

- The top band: the brand mark, the pill bar, the week chip, the actions, and the theme button. It is sticky, so it stays on screen at every scroll. The actions are the button of each package of the client, such as the egg button, which the app passes.
- The pill bar: each destination with its full label, from the desktop tier up. The dock: each destination as an icon and a short label, fixed at the bottom of a phone and a tablet. It tucks away while a field that calls `useKeyboardField` of `keyboard.ts` has the focus, and the root then holds `data-keyboard` and `--keyboard-inset`, so a part that sticks to the foot sits right above the keyboard. `useKeyboardRaised` is true while that inset is a real keyboard, so a part that does not stick to the foot, such as the dock of an empty Thread, can pin itself above it. With `nav="sheet"`, a page with its own foot, such as the front door, has no dock and no week chip: a menu button opens a sheet of the pages under the band, which closes by the X, the dimmed page, Escape, or a swipe up. The page can add its own rows under the pages, each a `MenuRow` that acts on the page, such as the passphrase row of the front door.
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
