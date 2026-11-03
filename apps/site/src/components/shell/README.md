# src/components/shell: the shell of every page

## Knows

- The masthead, which renders an optional week line and the menu. It stays a server component.
- The menu button, the sheet, and the compact bar, in one client island of the masthead.
- The desktop row of the menu, with the Past weeks popover.
- The theme button, and the aria-current value of a menu link.

## Ports

- The theme choice in local storage, through `src/lib/theme.ts`.
- GoatCounter events, through `src/lib/usage.ts`.

## Does not do

- It builds no menu link and lists no week. `src/app/masthead-props.ts` builds them, and the masthead takes them as props.
- It sets no theme before the first paint. The root layout inlines the boot script from `src/lib/theme.ts`.
- It holds no chapter. Each page folder holds its chapters.
- It holds no primitive. The dialog and the popover come from `src/components/ui/`.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
