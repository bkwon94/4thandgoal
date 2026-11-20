# 01: Oxlint runs on the site code with the `@ui-sdk` rule

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-8, AT-9, and AT-13.

**App:** site

**What to build:** Oxlint lints all site code with one config. The hook lints the staged site files, and CI lints all site code in the site-unit job. The first rule is the built-in `no-restricted-imports`: an import of `@ui-sdk` passes only in the `ui` folder of the design package. The rule test of ADR 0035 goes away, and ADR 0035 gets one line that names ADR 0038. The local plugin of the design rules exists with no rule yet, and a rule test runs the lint on a fixture folder.

**Blocked by:** none

**Status:** ready-for-agent

- [x] A fixture file outside `ui` that imports `@ui-sdk/react` fails the lint with `no-restricted-imports` and its line.
- [x] A fixture file inside the fixture copy of `ui` that imports `@ui-sdk/react` passes.
- [x] The lint of all site code exits 0.
- [x] The config ignores only build output, test fixtures, and generated files.
- [x] The hook runs the lint on the staged site files, and CI runs it on all site code.
- [x] The `@ui-sdk` rule test no longer exists, and ADR 0035 names ADR 0038.
