# 07: notes on the ui-sdk Drawer in our build

Research for `07-research-ui-sdk-in-our-build.md`. Run on 2026-11-14.

## How the runs worked

1. A throwaway detached worktree of `ui-sdk-sheet` at `79a4ed48`, in the session scratchpad. It is removed. `git worktree list` no longer shows it.
2. `corepack pnpm@10.12.4 install`, then `corepack pnpm@10.12.4 add @ui-sdk/react@0.1.0-beta.1 @ui-sdk/core@0.1.0-beta.1` in `apps/site`.
3. A probe client component on `/rankings/`: `<Drawer side="top">` with a trigger, a backdrop, a title, a close button, and a 40-row inner scroll area (`min-h-0 flex-1 overflow-y-auto`). Tailwind classes style each part. No `web.css`.
4. `@layer ui-sdk;` added as the first rule of `apps/site/src/app/globals.css`, above `@import "tailwindcss"`.
5. `CLIENT=cpc pnpm build` before and after, on Node 24.13.1. Next 16.4.2 with Turbopack.
6. Playwright 1.64.1 with Chromium, against the static `out/` served by `python3 -m http.server`. Three contexts: desktop mouse, desktop with `reducedMotion: "reduce"`, and a 390 x 844 phone with `hasTouch` and `isMobile`. Touch gestures went through CDP `Input.dispatchTouchEvent`.
7. `next dev` on the probe, to see the hydration warnings that only a dev build prints.

Node: `pnpm add` wrote exact versions, `"0.1.0-beta.1"`, with no caret.

## 1. Server render and hydration

**Answer: yes.** The `Drawer` renders on the server in the static export and hydrates with no warning, in the production build and in `next dev`.

Evidence:

- The build printed no warning and no error. TypeScript passed. All 24 static pages generated. Command: `CLIENT=cpc pnpm build`. Neither log matches `grep -i -E 'warn|error'`.
- `out/rankings/index.html` holds the trigger as server HTML: `data-slot="drawer-trigger" aria-haspopup="dialog" data-closed="" type="button"`. The closed content is not in the HTML (`grep -c probe-content` gives 0). It mounts on open.
- The console of the production page holds the same three lines before and after the probe. They are a goatcounter warning for localhost and a CORS failure of the egg board fetch. Neither comes from the `Drawer`. No React error #418 or #423.
- `next dev` with the probe printed no hydration warning in the browser console, and no warning in the server log. It printed only the React DevTools note, `[HMR] connected`, and the same goatcounter and CORS lines.
- The docs agree. `node_modules/@ui-sdk/react/docs/server-rendering.md`: "ui-sdk parts render their initial HTML on the server", and the modules "already include `\"use client\"`". Popups "render in place, so they don't need a portal root".
- The open sheet is in the top layer: the viewport matches `:popover-open` or `:modal` (probe output `viewportPopover: true`).

## 2. `@layer ui-sdk;` with Tailwind 4

**Answer: yes, it works.** The built CSS keeps the line, and Tailwind utilities win over the ui-sdk rules on the open sheet. One detail: Tailwind emits its `properties` layer before our line.

Evidence:

- The docs ask for it. `node_modules/@ui-sdk/react/docs/styling-and-animation.md`, section "The ui-sdk Layer": "With Tailwind, put it above `@import \"tailwindcss\"`".
- Layer order in the built CSS file, read with `grep -o '@layer [a-z, -]*[;{]'`:
  - Before: `@layer properties{ @layer theme{ @layer base{ @layer components{ @layer utilities{`
  - After: `@layer properties{ @layer ui-sdk; @layer theme{ @layer base{ @layer components{ @layer utilities{`
- So the order is `properties`, `ui-sdk`, `theme`, `base`, `components`, `utilities`. The `properties` layer holds only the `--tw-*` fallbacks for `@property`. The ui-sdk rules set no `--tw-*` value, so this order causes no conflict.
- At run time ui-sdk adds two `<style>` tags at the start of `<head>`, before the CSS link of the page. Each one wraps its rules in `@layer ui-sdk { ... }`. One rule resets `inset`, `padding`, `background`, and other values on `[data-slot="drawer-content"][popover]`.
- The cascade check on the open sheet: computed `padding` is `16px` (from `p-4`), `background-color` is the `bg-neutral-900` color, and `max-height` is `504px` (from `max-h-[70dvh]`). Tailwind wins.
- In Chromium the ui-sdk `<style>` tags come first in the document, so the layer is first even with no line in `globals.css`. The line matters on the other path. With a CSP meta tag that has no nonce, ui-sdk uses `adoptedStyleSheets`, which come after the document sheets (`styling-and-animation.md`, "Content Security Policy"). Keep the line, as decision 06 says.
- The repo has no `Content-Security-Policy` header. `grep -rIl -i content-security-policy` outside `node_modules`, `.next`, and `out` found nothing.
- The CSS file grew by 601 bytes raw, from 118,318 to 118,919. That is the Tailwind classes of the probe plus the line.

## 3. Bundle cost

**Answer: about 43 KB gzip, or about 39 KB brotli, for one page.** The menu sheet sits in `TopBand`, on every page, so a direct import adds that cost to every page.

Evidence. Script: sum each `/_next/static/**/*.js` that the HTML of the page loads, with gzip level 9 and brotli quality 11.

| Page | Chunks | Raw | Gzip | Brotli |
| --- | --- | --- | --- | --- |
| `/rankings/` before | 8 | 1,094,808 | 318,118 | 263,973 |
| `/rankings/` after | 10 | 1,213,970 | 361,597 | 303,394 |
| Delta | +2 | +119,162 | +43,479 | +39,421 |

- The other pages (`/`, `/eggs/`, `/2026/week-09/`) did not change. So the cost stays with the page that imports the `Drawer`.
- Three new chunks replaced one changed chunk: 80,692 raw and 29,325 gzip, 38,290 raw and 14,165 gzip, 13,636 raw and 4,761 gzip.
- `menu-sheet.tsx` imports only `lucide-react`, React, and local files. It uses no `framer-motion`. So the move removes no library to offset the cost.
- The delta holds the `Drawer` entry and the parts of `@ui-sdk/core` it pulls in: dialog, popups, sheet drivers, and motion. A later ui-sdk component may share part of it. This run does not measure that share.
- `@ui-sdk/react` declares `"sideEffects": false` and has no root entry. Each part imports from its own path, such as `@ui-sdk/react/drawer` (`package.json`, `docs/installation.md`).

## 4. Beta churn and the pin

**Answer: too early to tell.** The beta is two days old and has one patch release, with no API break. A pin costs a manual bump of two packages together.

Evidence:

- npm registry, `https://registry.npmjs.org/@ui-sdk%2Freact` and `.../@ui-sdk%2Fcore`:
  - `0.1.0-beta.1` published 2026-11-12.
  - `0.1.0-beta.2` published 2026-11-13.
  - The dist-tags are `latest: 0.1.0-beta.1` and `beta: 0.1.0-beta.2`.
- Release notes, https://github.com/vercel-labs/ui/releases/tag/%40ui-sdk/react%400.1.0-beta.2 and https://github.com/vercel-labs/ui/releases/tag/%40ui-sdk/core%400.1.0-beta.2. Each has "Patch Changes" only:
  - react: a disabled `Button` as a router link no longer navigates, and a `SelectTrigger` gets its field label in the server HTML.
  - core: a modal opened over another modal is not made inert, and the preference script reads the first of two cookies with one name.
  - No change touches the `Drawer`.
- `packages/react/CHANGELOG.md` on `main` of `vercel-labs/ui`: `0.1.0-beta.1` is "Initial release". `0.1.0-beta.2` is the patch list above.
- Pending work on `main`: `.changeset/` holds two more patch changesets for core, `listbox-restore-guard.md` and `webmcp-improvements.md`. Neither touches the `Drawer`. `.changeset/pre.json` sets prerelease mode with the tag `beta`. Command: `gh api repos/vercel-labs/ui/contents/.changeset`.
- The types mark stability per export. In `@ui-sdk/core/dist`, `.d.ts` files hold 1,019 `@stable`, 363 `@experimental`, and 35 `@internal` tags. `components/drawer/drawer.d.ts` has 17 `@stable` and 0 `@experimental`. `foundation/motion/physics.d.ts` (`SheetPhysics`) has 2 `@stable`. The docs do not define what `@stable` promises in a beta.

What a pin costs:

- `pnpm add` already writes the exact version. The lockfile pins it too.
- The peer range of `@ui-sdk/react` is `"@ui-sdk/core": "^0.1.0-beta.1"`. That range lets core drift to any later `0.1.0` prerelease or `0.1.x`. So pin both packages exact, and bump them together.
- The repo has no Renovate or Dependabot config. `.github/` holds only workflows. So each bump is a manual change, with a read of the release notes.
- The site already pins exact versions: `ai`, `@ai-sdk/react`, and `unicode-animations`. A pin of ui-sdk matches that habit.
- Today a bump means `0.1.0-beta.2`, which fixes nothing we use.

## 5. `side="top"`, the driver, the scroll, and reduced motion

**Answer: yes, `side="top"` uses the pointer driver on every device. An inner scroll scrolls first, and the same gesture closes the sheet once the list is at its end. Under reduced motion the sheet fades over 150 ms and does not slide, which matches ADR 0034.**

Driver evidence:

- `docs/components/drawer.md`, "Driver and Physics": `"auto"` chooses native scrolling for a bottom sheet on a touch screen, "and pointer dragging for mouse and pen, other sides, `modalAbove`, or `expandOnScroll` false".
- `@ui-sdk/core/dist/foundation/popups/sheet-driver.d.ts`: `"auto"` "picks scroll snap for a bottom sheet on a touch screen, and the pointer driver otherwise".
- The run: `data-driver="pointer"` and `data-side="top"` on the open content, in the desktop context and in the phone context with touch.
- The open motion on the pointer driver is a spring sampled into `linear()`, on `translate`. Desktop: 510 ms, `translate: 0px -592px` to `0px`. Phone: 513 ms, `0px -623px` to `0px`. Three registered variables, `--drawer-progress`, `--drawer-dim`, and `--drawer-expand`, animate with it.
- The spring is tunable with `physics`, which overrides part of `sheetPhysics.ios`: `response`, `dampingRatio`, `momentumDampingRatio`, `projectionRate`, `minFlingVelocity`, and `skipSnapPoints` (`foundation/motion/physics.d.ts`). This matches the first consequence of ADR 0034.

Scroll evidence:

- `foundation/popups/sheet-axis.d.ts`, `scrollContext`: "`atStart` means it can't scroll further the way a finger moving toward the edge scrolls it". The function takes the side. For a top sheet the edge is up, so a finger that moves up scrolls the list forward. The sheet takes over only when the list is at its end.
- `docs/components/drawer.md`, "Scrollable Content", says the same for a bottom sheet: "A downward drag scrolls that area first; when it reaches the top, the same gesture can move the drawer."
- The run on the phone context, with a list of 922 px of overflow:
  1. A slow upward swipe on the list: `scrollTop` 0 to 279. The sheet stays open.
  2. The list set to its end: `scrollTop` 922.
  3. An upward swipe: the sheet closes and unmounts (`open: false, present: false`).
- What that means for the menu sheet: a long list inside it scrolls normally. A user who scrolls to the end of the list and keeps the swipe going closes the sheet. A mouse drag starts only on the handle or on empty space (`canMouseDrag` in `sheet-driver.d.ts`), so a mouse never drags the sheet from the list.

Reduced-motion evidence:

- `docs/components/drawer.md`: "The drawer respects reduced motion, fading instead of sliding." The tested behavior list also says "With reduced motion it fades in and out instead of sliding."
- `foundation/popups/sheet-driver.d.ts` declares `reducedFade = 150` and `reducedSettle = 200`.
- The run with `reducedMotion: "reduce"`:
  - Open: one animation on the content, `opacity` 0 to 1, 150 ms, `linear`. No `translate` keyframes.
  - Close with Escape: `opacity` 1 to 0, 150 ms. No `translate` keyframes.
- ADR 0034: "Under reduced motion, a sheet fades and does not slide." The run matches it. ADR 0034 sets no fade time, so 150 ms is within the rule.

## Risks and open points

- **Real devices: not confirmed.** All runs used desktop Chromium. The touch run emulated touch through CDP. iOS Safari and Android Chrome may differ in the scroll handoff, the toolbar bleed, and the top layer. Ticket 08 should test them on a phone.
- **`reducedSettle = 200`: not confirmed.** The constant exists in `sheet-driver.d.ts`. The runs did not show where it applies. It may be a settle after a drag release under reduced motion. If it moves `translate`, it is motion under reduced motion. A drag under the finger follows the finger, so ADR 0034 likely allows it. Check it in ticket 08.
- **The menu-sheet height with the scroll handoff.** If the menu list fits with no overflow, any upward swipe on it moves the sheet. This is expected, but ticket 08 should feel it.
- **The bundle cost on every page.** A direct import in `TopBand` adds about 43 KB gzip to each page. A lazy import on the first tap may cut it. The runs did not test a lazy import, and a lazy import may delay the first open.
- **Shared core cost: not confirmed.** The run measured one component. How much of the 43 KB a second ui-sdk component reuses is unknown.
- **Beta churn: not confirmed past two days.** One patch release is too little history to judge the break rate. The docs do not define what `@stable` promises before `0.1.0`.
- **`next dev` writes to `apps/site/AGENTS.md`.** Next 16.4 adds a `nextjs-agent-rules` block to `apps/site/AGENTS.md` on each `next dev` run. It is not caused by ui-sdk. An agent that runs `pnpm dev` in a ticket worktree must not commit it by accident.
- **Firefox and WebKit: not confirmed.** The `@layer` order and the head position of the ui-sdk `<style>` tags were checked in Chromium only.
