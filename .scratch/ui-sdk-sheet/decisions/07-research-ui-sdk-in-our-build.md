# 07: Does the ui-sdk Drawer work in our build?

Map: `.scratch/ui-sdk-sheet/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The site is a Next 16 static build with React 19, Tailwind 4, and `framer-motion`. ui-sdk is at `0.1.0-beta.1`. Find out:

1. If the `Drawer` renders on the server and hydrates with no warning in our static build.
2. If the `@layer ui-sdk;` order works with Tailwind 4 and `globals.css`.
3. How much the `Drawer` entry adds to the client bundle of a page.
4. How often the beta breaks its API, from the changelog, and what a pin costs us.
5. If `side="top"` uses the pointer driver, and what that means for a scroll inside the sheet.

The spec needs these facts before it can promise a shipped move. Write the findings to `07-research-ui-sdk-in-our-build.notes.md`.

## Decision

The ui-sdk `Drawer` works in our build. The spec can promise a shipped move. The notes are in `07-research-ui-sdk-in-our-build.notes.md`.

1. The static build of `cpc` and `next dev` print no warning and no hydration error.
2. `@layer ui-sdk;` above `@import "tailwindcss"` works. Our Tailwind classes win over the ui-sdk reset.
3. The `Drawer` adds about 43 KB gzip to each page that imports it. `TopBand` is on every page, so a direct import adds it to every page. Decision 10 decides this cost.
4. The beta is too new to judge its churn. Pin `@ui-sdk/react` and `@ui-sdk/core` to one exact version, and bump them together by hand. The react package accepts any later core beta, so both pins matter.
5. `side="top"` uses the pointer driver with a spring. A swipe scrolls the inner list first, then closes the sheet. Under reduced motion, the sheet fades in 150 ms with no slide, as ADR 0034 says.

Not confirmed: real iOS and Android devices, Firefox, and WebKit. Ticket 08 checks the phone. `next dev` in Next 16.4 adds a block to `apps/site/AGENTS.md`; a ticket must not commit it.

An Opus research agent found the facts on 2026-11-14 with a real build in a throwaway worktree.
