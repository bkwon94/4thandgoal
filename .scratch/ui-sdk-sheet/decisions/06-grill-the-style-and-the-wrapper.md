# 06: How do we style ui-sdk, and where do the wrappers live?

Map: `.scratch/ui-sdk-sheet/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

ui-sdk renders no styles and offers an optional default look, `web.css`. Each package could import it directly, or through one wrapper.

## Decision

No `web.css`, because the look of ADR 0024 owns the components. Tailwind styles each part on `data-slot`, the state attributes, and the CSS variables. Each ui-sdk part gets one wrapper in `packages/design/site/ui/`, such as `ui/sheet.tsx`, and no other package imports `@ui-sdk`. `globals.css` declares `@layer ui-sdk;` above `@import "tailwindcss"`. Brian decided it in the grill of 2026-11-14.
