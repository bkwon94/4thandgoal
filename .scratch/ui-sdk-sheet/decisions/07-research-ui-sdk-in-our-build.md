# 07: Does the ui-sdk Drawer work in our build?

Map: `.scratch/ui-sdk-sheet/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

The site is a Next 16 static build with React 19, Tailwind 4, and `framer-motion`. ui-sdk is at `0.1.0-beta.1`. Find out:

1. If the `Drawer` renders on the server and hydrates with no warning in our static build.
2. If the `@layer ui-sdk;` order works with Tailwind 4 and `globals.css`.
3. How much the `Drawer` entry adds to the client bundle of a page.
4. How often the beta breaks its API, from the changelog, and what a pin costs us.
5. If `side="top"` uses the pointer driver, and what that means for a scroll inside the sheet.

The spec needs these facts before it can promise a shipped move. Write the findings to `07-research-ui-sdk-in-our-build.notes.md`.

## Decision

None yet.
