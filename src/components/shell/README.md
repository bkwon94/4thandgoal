# components/shell: the shell of every page

## Knows

- The masthead: the brand link, the page line, the week line, and the menu.
- The menu: the menu button, the sheet, the desktop row with the Past weeks popover, and the compact bar.
- The theme button, and the aria-current value of a menu link.

## Ports

- The theme choice in local storage, through `lib/theme.ts`.
- GoatCounter events, through `lib/usage.ts`.

## Does not do

- It builds no menu link and lists no week. `src/app/masthead-props.ts` builds them, and the masthead takes them as props.
- It sets no theme before the first paint. The root layout inlines the boot script from `lib/theme.ts`.
- It holds no chapter. Each page folder holds its chapters.
- It holds no primitive. The dialog and the popover come from `components/ui/`.
- It reads no file, no env, and no config, and it calls no loader (ADR 0004).
