# 04: Reads leave the masthead, the home page, and the layout

**What to build:** The masthead takes its week summaries and its links as required props. The home page, the layout, and every route file call the loaders and the route builders in the app layer and pass values down. The usage code comes to the layout as a value from the app layer. This closes manager-pages site ticket 12.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] The masthead has no default prop that calls a loader. Its props are required.
- [ ] No file under the components folder imports a loader or the config module. A grep proves it.
- [ ] Every route file is the only place that calls a loader for its page.
- [ ] `pnpm typecheck`, `pnpm test`, and `pnpm check:export` pass. `out/` has no diff against `main`.
