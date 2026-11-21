# 01: Oxlint runs on the site code with the `@ui-sdk` rule

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-8, AT-9, and AT-13.

**App:** site

**What to build:** Oxlint lints all site code with one config. The hook lints the staged site files, and CI lints all site code in the site-unit job. The first rule is the built-in `no-restricted-imports`: an import of `@ui-sdk` passes only in the `ui` folder of the design package. The rule test of ADR 0035 goes away, and ADR 0035 gets one line that names ADR 0038. The local plugin of the design rules exists with no rule yet, and a rule test runs the lint on a fixture folder.

**Blocked by:** none

**Status:** done

- [x] A fixture file outside `ui` that imports `@ui-sdk/react` fails the lint with `no-restricted-imports` and its line.
- [x] A fixture file inside the fixture copy of `ui` that imports `@ui-sdk/react` passes.
- [x] The lint of all site code exits 0.
- [x] The config ignores only build output, test fixtures, and generated files.
- [x] The hook runs the lint on the staged site files, and CI runs it on all site code.
- [x] The `@ui-sdk` rule test no longer exists, and ADR 0035 names ADR 0038.

## Comments

The merge: `856b2c0d` merged into `design-checks-speed` on 2026-11-20; review fixes on fix branches a to n; Judge fix round on AT-13 (evidence only).
The proof: `make check-fast BASE=main` passed at each merge, 3 green CI runs on 4d5f4d13 gave a median of 315 s, and the Judge gave PASS to AT-1 to AT-39.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/design-checks-speed/PRD.md, .scratch/design-checks-speed/ACCEPTANCE.md, .scratch/design-checks-speed/issues/01-oxlint-and-the-ui-sdk-rule.md.
Closes with the squash merge of the spec PR.
