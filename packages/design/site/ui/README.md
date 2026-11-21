# packages/design/site/ui: the shadcn primitives

## Knows

- The button, the collapsible, the dialog, the input, the label, the popover, the scroll area, the segmented control, the select, the sheet, the stop card, and the toggle group. Most of them wrap a Base UI primitive and add the site styles.
- The sheet wraps the ui-sdk `Drawer`: root, trigger, backdrop, content, grip, title, and close. `sheet.tsx` imports `@ui-sdk`. The content of a top or bottom sheet has a bleed past its anchored edge. A drag past the open height stretches the sheet a little, and the bleed keeps that edge on the screen.
- The pending button wraps the ui-sdk `Button`. `pending-button.tsx` is the second file that imports `@ui-sdk`. It has its own name because `button.tsx` is the shadcn button.
- The toggle group wraps the ui-sdk `Toggle` and `ToggleGroup`. `toggle-group.tsx` is the third file that imports `@ui-sdk`.
- The scroll area wraps the ui-sdk `ScrollArea`: root, viewport, and content. `scroll-area.tsx` imports `@ui-sdk`. The viewport is the native scroller and hides its scrollbar, so a part sets only its size, mask, and padding.
- The segmented control wraps the ui-sdk `SegmentedControl`: root, sliding indicator, and items. `segmented-control.tsx` imports `@ui-sdk`. The items split the full width in equal parts, the pill slides in 250 ms with the brand ease-out, and `tone="dark"` sets it on a hero.
- The collapsible wraps the ui-sdk `Collapsible`: root, trigger, and panel. `collapsible.tsx` imports `@ui-sdk`. The panel animates its height, and reduced motion opens it at once.
- The stop card wraps the ui-sdk `Popover` for the Tour: root, content, title, and line. It is modal, has no trigger, and never turns into a sheet. `stop-card.tsx` imports `@ui-sdk`. It has its own name because `popover.tsx` is the Base UI popover.
- `SheetGrip` is the plain bar that shows a sheet drags. A sheet with one snap point takes it, not the handle button of the `Drawer`. `sheet-jsdom.ts` holds the jsdom stand-ins that a test imports before it opens the sheet.
- The label is the form label. The red label that opens a chapter is `site/parts/label.tsx`.

## Ports

None.

## Does not do

- It knows no league term. A component that shows a team, a player, or a week is a part in `site/parts/`, or it lives in its page folder.
- It holds no state of the site and no `cn` helper. `site/lib/utils.ts` holds the helper.
- No file outside this folder imports `@ui-sdk`. The rule test `apps/site/src/ui-sdk-rule.test.ts` fails on one.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
