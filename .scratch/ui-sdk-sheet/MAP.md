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

## NOT YET SPECIFIED

- Does the ui-sdk `Drawer` work in our static build, with Tailwind 4, at an OK bundle cost? `decisions/07-research-ui-sdk-in-our-build.md`.
- How does the menu sheet feel as a `Drawer`: snap points, handle, physics? `decisions/08-prototype-the-feel-of-the-menu-sheet.md`.
- Which `package.json` declares ui-sdk, and which rule test guards the wrapper rule? `decisions/09-spec-the-guard-and-the-dependency.md`.

## OUT OF SCOPE

- The other four sheets: `player-sheet`, `claim-sheet`, `team-sheet`, and `passphrase-sheet`. Each one copies the rules in its own spec after this one ships.
- `side-tabs`, `show-all`, `index-list`, and other hand-built controls. The same reason.
- The ui-sdk default look, `web.css`. The look of ADR 0024 owns the components (decision 06).
- The pill bar of the desktop. It is no sheet, and it works.
