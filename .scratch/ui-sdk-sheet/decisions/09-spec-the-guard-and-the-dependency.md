# 09: Where does the ui-sdk dependency live, and what guards the wrapper rule?

Map: `.scratch/ui-sdk-sheet/MAP.md`.

**Kind:** spec

**Blocked by:** 06

**Status:** done

## Question

Decision 06 says only `packages/design/site/ui/` imports `@ui-sdk`. The spec records two small choices:

1. Which `package.json` declares `@ui-sdk/react` and `@ui-sdk/core`: `packages/design/site/package.json`, `apps/site/package.json`, or both.
2. Which rule test fails an import of `@ui-sdk` outside `packages/design/site/ui/`, beside `apps/site/src/component-rule.test.ts`.

## Decision

The `package.json` of the design package declares `@ui-sdk/react` and `@ui-sdk/core`, each pinned to one exact version. The site app gets them through its workspace dependency, so it does not declare them. A rule test beside `apps/site/src/component-rule.test.ts` fails an import of `@ui-sdk` outside `packages/design/site/ui/`, through the shared rule report. `PRD.md` records both under Implementation Decisions. Brian approved the spec on 2026-11-14.
