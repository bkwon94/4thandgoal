# The .ts files of the two folders, which the table leaves out because they are not .tsx files:
$ git ls-files "packages/design/site/ui/*.ts" "packages/design/site/parts/*.ts" | grep -v test
packages/design/site/parts/drift-scene.ts
packages/design/site/parts/mesh-canvas.ts
packages/design/site/parts/mesh-math.ts
packages/design/site/parts/scene-canvas.ts
packages/design/site/parts/scene-math.ts
packages/design/site/parts/scene-motion.ts
packages/design/site/ui/sheet-drag-jsdom.ts
packages/design/site/ui/sheet-jsdom.ts

$ grep -n -A3 '^## Knows' packages/design/site/ui/README.md
3:## Knows
4-
5-- The button, the collapsible, the dialog, the input, the label, the popover, the segmented control, the select, the sheet, the stop card, and the toggle group. Most of them wrap a Base UI primitive and add the site styles.
6-- The sheet wraps the ui-sdk `Drawer`: root, trigger, backdrop, content, grip, title, and close. `sheet.tsx` imports `@ui-sdk`. The content of a top or bottom sheet has a bleed past its anchored edge. A drag past the open height stretches the sheet a little, and the bleed keeps that edge on the screen.

$ grep -n -A3 '^## Knows' packages/design/site/parts/README.md
3:## Knows
4-
5-- The chapter, the label, the tag, the blurb, and the team name.
6-- The page column, which a wide page widens to the top band from the desktop tier, and the chapter rail.

