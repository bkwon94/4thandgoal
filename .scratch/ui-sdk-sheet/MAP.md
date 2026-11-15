# ui-sdk sheet: map

App: site.
Spec branch: `ui-sdk-sheet`.

## DESTINATION

The menu sheet runs on the ui-sdk `Drawer` on the live site, with a native feel of drag, spring, and snap on every device. The spec also records the rules that later moves to ui-sdk copy: one wrapper in `packages/design/site/ui/`, Tailwind styles, and ADR 0034 for motion.

## DECISIONS SO FAR

- The spec moves one component to ui-sdk on the live site and records the adoption rules. `decisions/01-grill-the-destination.md`.
- The goal is the feel on every device, with the phone first. `decisions/02-grill-the-goal.md`.
- `menu-sheet` moves first. `decisions/03-grill-the-first-component.md`.
- A Sheet moves in from any edge, the Menu gets the menu sheet as a third form, and "Drawer" stays out of prose. `decisions/04-grill-the-names.md`.
- A sheet you can drag follows a spring and may fade under reduced motion (ADR 0034). `decisions/05-grill-the-motion-rule.md`.
- No `web.css`; Tailwind styles one wrapper per part in `packages/design/site/ui/`. `decisions/06-grill-the-style-and-the-wrapper.md`.
- The `Drawer` works in our static build and with Tailwind 4; pin both packages exact; it costs about 43 KB gzip per page. `decisions/07-research-ui-sdk-in-our-build.md`.
- The menu sheet drops from the top with one snap point, a grab handle, the default iOS physics, and a dim with no page scale. `decisions/08-prototype-the-feel-of-the-menu-sheet.md`.
- Only the front door pays the `Drawer`, with a direct import; one acceptance test shows a dock page does not grow. `decisions/10-grill-the-bundle-cost.md`.
- The design package alone declares ui-sdk, pinned exact; a rule test fails an import of ui-sdk outside its ui folder. `decisions/09-spec-the-guard-and-the-dependency.md`.

## NOT YET SPECIFIED

None.

## OUT OF SCOPE

- The other four sheets: `player-sheet`, `claim-sheet`, `team-sheet`, and `passphrase-sheet`. Each one copies the rules in its own spec after this one ships.
- `side-tabs`, `show-all`, `index-list`, and other hand-built controls. The same reason.
- The ui-sdk default look, `web.css`. The look of ADR 0024 owns the components (decision 06).
- The pill bar of the desktop. It is no sheet, and it works.
- The dock. It is no sheet, and it works (decision 10).
- A standing check of the bundle size in CI. It is its own feature (decision 10).
- A mouse drag on a row of the sheet on desktop. The native drag of the link stops it in the current sheet too, and touch works (decision 08).
