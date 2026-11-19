# packages/design/site/ui: the shadcn primitives

## Knows

- The button, the dialog, the input, the label, the popover, the select, the sheet, and the toggle group.
- Most of them wrap a Base UI primitive and add the site styles.
- The sheet wraps the ui-sdk `Drawer`: root, trigger, backdrop, content, grip, title, and close. `sheet.tsx` imports `@ui-sdk`.
- The pending button wraps the ui-sdk `Button`. `pending-button.tsx` is the second file that imports `@ui-sdk`. It has its own name because `button.tsx` is the shadcn button.
- The toggle group wraps the ui-sdk `Toggle` and `ToggleGroup`. `toggle-group.tsx` is the third file that imports `@ui-sdk`.
- `SheetGrip` is the plain bar that shows a sheet drags. A sheet with one snap point takes it, not the handle button of the `Drawer`.
- `sheet-jsdom.ts` holds the jsdom stand-ins that a test imports before it opens the sheet.
- The label is the form label. The red label that opens a chapter is `site/parts/label.tsx`.

## Ports

None.

## Does not do

- It knows no league term. A component that shows a team, a player, or a week is a part in `site/parts/`, or it lives in its page folder.
- It holds no state of the site.
- It holds no `cn` helper. `site/lib/utils.ts` holds it.
- No file outside this folder imports `@ui-sdk`. The rule test `apps/site/src/ui-sdk-rule.test.ts` fails on one.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
