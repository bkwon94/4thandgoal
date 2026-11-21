# The two use lines of each component file of packages/design/site/ui/ and packages/design/site/parts/

Made with a script that reads the first block comment of each `*.tsx` file that is not a `.test.tsx` file, and prints each line that starts with `Use it when:` or `Do not use it when:`. A `-` means the docstring has no such line. Each docstring line keeps its full text; a line that wraps to the next docstring line shows only its first line.

| File | Use it when | Do not use it when |
| --- | --- | --- |
| `packages/design/site/ui/button.tsx` | Use it when: you need a pressable action in the site style. `variant="plain"` keeps only the given className. | Do not use it when: the action runs async and must show it waits. Use `PendingButton`. |
| `packages/design/site/ui/collapsible.tsx` | Use it when: one trigger shows and hides one panel. | Do not use it when: a card opens in place. Use `OpenCard`. |
| `packages/design/site/ui/dialog.tsx` | Use it when: a centered modal needs an answer from the reader. | Do not use it when: the panel comes from an edge and drags closed. Use `Sheet`. |
| `packages/design/site/ui/input.tsx` | Use it when: the reader types one line of text. | Do not use it when: the reader picks from a list. Use `Select`. |
| `packages/design/site/ui/label.tsx` | Use it when: a form field needs its label. | Do not use it when: the label opens a chapter or a card. Use `Label` in `site/parts/label.tsx`. |
| `packages/design/site/ui/pending-button.tsx` | Use it when: a press starts async work and the button must wait until it ends. | Do not use it when: the action ends at once. Use `Button`. |
| `packages/design/site/ui/popover.tsx` | Use it when: a popup opens from a trigger and sits next to it. | Do not use it when: the popup is a stop of the Tour. Use `StopCard`. |
| `packages/design/site/ui/segmented-control.tsx` | Use it when: the reader picks one of two to four modes of one view, and the pill slides to the pick. | Do not use it when: each choice toggles on its own, or the choices are many. Use `ToggleGroup` or `Select`. |
| `packages/design/site/ui/select.tsx` | Use it when: the reader picks one or many items from a list. | Do not use it when: the choices are few and the reader sees all of them. Use `ToggleGroup`. |
| `packages/design/site/ui/sheet.tsx` | Use it when: a panel comes in from an edge and the reader drags it closed. | Do not use it when: the panel is a centered modal. Use `Dialog`. |
| `packages/design/site/ui/stop-card.tsx` | Use it when: a step of the Tour points at one element. | Do not use it when: a popup opens from a trigger. Use `Popover`. |
| `packages/design/site/ui/toggle-group.tsx` | Use it when: the reader picks from a few choices that all show. | Do not use it when: the list is long. Use `Select`. |
| `packages/design/site/parts/announcement.tsx` | Use it when: one new feature needs a one-time introduction. | Do not use it when: the sheet needs an answer from the reader. Use `Dialog`. |
| `packages/design/site/parts/bar-fill.tsx` | Use it when: a bar needs a fill at its percent that grows once. | Do not use it when: the bars show a week series. Use the Trend tile in `Tile`. |
| `packages/design/site/parts/blurb.tsx` | Use it when: a short paragraph sits under a chapter label or a grid of cards. | Do not use it when: the text needs a surface of its own. Use `Card`. |
| `packages/design/site/parts/card.tsx` | Use it when: one item needs a plain surface on the page. | Do not use it when: the card opens and closes in place. Use `OpenCard`. |
| `packages/design/site/parts/chapter-rail.tsx` | Use it when: a week page needs links to its chapters beside the column. | Do not use it when: the page has no chapters to link. |
| `packages/design/site/parts/chapter.tsx` | Use it when: one topic of a page needs its own section. | Do not use it when: the group sits inside a chapter. Use `Card`. |
| `packages/design/site/parts/error-line.tsx` | Use it when: a form or a dialog shows one error message. | Do not use it when: the text is not an error. Use `Blurb`. |
| `packages/design/site/parts/hero-mesh.tsx` | Use it when: a hero needs the live grid art as its `art`. | Do not use it when: the hero shows a scene of a matchup. Use `HeroSceneCanvas`. |
| `packages/design/site/parts/hero-scene.tsx` | Use it when: the first hero of a page shows a scene. | Do not use it when: the hero shows the grid art. Use `HeroMesh`. |
| `packages/design/site/parts/hero.tsx` | Use it when: a page needs its one loud top surface. | Do not use it when: the page has no hero. Use `WeekLine`. |
| `packages/design/site/parts/label.tsx` | Use it when: a red label opens a chapter or a card. | Do not use it when: the label names a form field. Use `Label` in `site/ui/label.tsx`. |
| `packages/design/site/parts/open-card.tsx` | Use it when: a card opens and closes in place. | Do not use it when: the card stays closed or open all the time. Use `Card`. |
| `packages/design/site/parts/page-column.tsx` | Use it when: a page needs the shared shell that centers its content. | Do not use it when: the block sits inside a chapter. The page column holds the chapters. |
| `packages/design/site/parts/photo-frame.tsx` | Use it when: a headshot or a team avatar needs a round frame. | Do not use it when: the image is art and not a person or a team. |
| `packages/design/site/parts/reveal.tsx` | Use it when: one block fades and rises in once. | Do not use it when: the whole page enters in a stagger. Use `Rise`. |
| `packages/design/site/parts/rise.tsx` | Use it when: a page enters in a stagger on load. | Do not use it when: one block fades in when it comes into view. Use `Reveal`. |
| `packages/design/site/parts/tag.tsx` | Use it when: a small red tag follows a label. | Do not use it when: the text is a note under a number. Use the note of `Tile`. |
| `packages/design/site/parts/team-name.tsx` | Use it when: a team name links to its manager page when the season has one. | Do not use it when: the text is not a team name. |
| `packages/design/site/parts/tile.tsx` | Use it when: one number needs a label above it and an optional note. | Do not use it when: the content is a row or prose. Use `Card`. |
| `packages/design/site/parts/week-line.tsx` | Use it when: a page with no hero needs the big week line. | Do not use it when: the page has a hero. Use `Hero`. |
