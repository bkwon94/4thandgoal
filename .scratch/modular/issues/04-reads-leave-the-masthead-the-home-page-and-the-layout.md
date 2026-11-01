# 04: Reads leave the masthead, the home page, and the layout

**What to build:** The masthead takes its week summaries and its links as required props. The home page, the layout, and every route file call the loaders and the route builders in the app layer and pass values down. The usage code comes to the layout as a value from the app layer. Manager-pages site ticket 12 closes with ticket 05, which takes the hand-built manager link out of the week parts.

**Blocked by:** 03

**Status:** done

- [ ] The masthead has no default prop that calls a loader. Its props are required.
- [x] No file under the components folder imports a loader. A grep proves it. The config imports in six files go in ticket 05, which names them.
- [ ] Every route file is the only place that calls a loader for its page.
- [x] `pnpm typecheck`, `pnpm test`, and `pnpm check:export` pass. The HTML markup has no diff against `main`. The inline flight data differs on every page, because the menu now takes its brand hrefs as props and React serializes a client prop.

## Comments

- 2026-10-31: merged into `main` from branch `modular-04-app-reads`, commits 7016d1e and ff922af. 514 tests. Two reviewers passed it after one fix pass. Noted drift: the loaders call route builders, which ADR 0004 reserves for the app layer; ticket 05 or a later one decides.
