# 03: The `lib/` split and the route builder

**What to build:** The lib splits by kind: a data folder for the four build-time loaders, the schemas folder from ticket 01, a format folder for the pure helpers, and one routes module. The routes module exports a builder per destination, home, rankings, analyze, week, waiver, managers, and one manager, each with the base path inside. The browser-only modules stay where they are. This ticket adds the builders and moves files. It changes no caller except the import paths.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] The four loaders sit in the data folder and are the only modules under lib that import the node fs.
- [ ] The routes module is the only module that joins the base path to a route. The href helpers in the loaders call it.
- [ ] Every pure helper sits in the format folder with a unit test.
- [ ] `pnpm typecheck`, `pnpm test`, and `pnpm check:export` pass. `out/` has no diff against `main`.
