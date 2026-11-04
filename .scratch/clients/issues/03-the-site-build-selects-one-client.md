# 03: The site build selects one client

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-6, AT-7, AT-18, AT-20, AT-21, AT-25, and AT-26.

**App:** site

**What to build:** The site builds one client, named by `CLIENT`. The build generates the routes, the registry of import lines, and the client values from `client.toml`, and copies only that client's published data. An omitted package is absent from the export.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] A build with no `CLIENT` exits non-zero and names `CLIENT` (AT-18).
- [ ] The `prebuild` step checks `client.toml` against the exported JSON Schema with `ajv`. An unknown key and a menu item for an omitted package each fail with a plain message (AT-20, AT-21).
- [ ] The `prebuild` step writes one route file per package, the registry, and the client values. Each generated file starts with a `GENERATED ... Do not edit.` line, and git ignores it (AT-25).
- [ ] The CPC published data lives in the client folder, and the build copies only it into the site. `check-export` still passes.
- [ ] The `cpc` export has no waiver route and no waiver JS (AT-6). The Trade Analyzer shows no finder (AT-7).
- [ ] `NEXT_PUBLIC_WAIVER`, `NEXT_PUBLIC_FINDER`, `NEXT_PUBLIC_SEASON`, and `NEXT_PUBLIC_USAGE_CODE` go away, and so does the `pageExtensions` gate.
- [ ] The publish stages only the published data of the client (AT-26). ADR 0019 and the root `CLAUDE.md` name the new publish path.
