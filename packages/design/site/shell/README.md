# packages/design/site/shell: the shell of every page

## Knows

- The masthead, which renders an optional week line and the menu. It stays a server component.
- The three menu layouts. The `hamburger` has the menu button, the sheet, the desktop row, and the compact bar.
- The `bar` wraps one row of links at every width. The `tabs` keep one row that scrolls sideways.
- The Past weeks popover of each layout, the theme button, and the aria-current value of a menu link.
- A brand with one set shows no theme button. A brand with no logo shows its title as text.
- The count script tag of the head.

## Ports

- The theme choice in local storage, through `site/lib/theme.ts`.
- GoatCounter events and the count script, through `site/lib/usage.ts`.

## Does not do

- It builds no menu link and lists no week. `apps/site/src/app/masthead-props.ts` builds the destinations.
- It sets no theme before the first paint. The root layout inlines the boot script from `site/lib/theme.ts`.
- It holds no chapter. Each page folder holds its chapters.
- It holds no primitive. The dialog and the popover come from `site/ui/`.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
