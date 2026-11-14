# 09: Where does the ui-sdk dependency live, and what guards the wrapper rule?

Map: `.scratch/ui-sdk-sheet/MAP.md`.

**Kind:** spec

**Blocked by:** 06

**Status:** open

## Question

Decision 06 says only `packages/design/site/ui/` imports `@ui-sdk`. The spec records two small choices:

1. Which `package.json` declares `@ui-sdk/react` and `@ui-sdk/core`: `packages/design/site/package.json`, `apps/site/package.json`, or both.
2. Which rule test fails an import of `@ui-sdk` outside `packages/design/site/ui/`, beside `apps/site/src/component-rule.test.ts`.

## Decision

None yet.
