# 01 notes: the parts that build the Tour

Research of 2026-11-18 for `decisions/01-research-the-tour-build.md`. Paths are from the worktree root.
`UI` is `node_modules/.pnpm/@ui-sdk+react@0.1.0-beta.2_@types+react@19.3.0_@ui-sdk+core@0.1.0-beta.2_react-dom@19.3.1_react@19.3.1__react@19.3.1/node_modules/@ui-sdk/react`.
`CORE` is `node_modules/.pnpm/@ui-sdk+core@0.1.0-beta.2/node_modules/@ui-sdk/core`.

## Recommendation

- **The Stop card is the ui-sdk `Popover`** with no trigger. Set `anchor` to the control of the Stop, `modal`, `dismissible={false}`, and `presentation="popover"`. A modal popover makes the page inert and locks scroll, so the real controls do not respond. `onDismissAttempt` with reason `outside-press` goes to the next Stop, and `escape-key` counts as Skip. It sits in the top layer above each z-index of the site.
- **Wrap it once in `packages/design/site/ui/`** under a new name, such as `ui/stop-card.tsx`. ADR 0035 lets only that folder import `@ui-sdk`. The file `ui/popover.tsx` is the Base UI popover, so the Tour cannot reuse that name.
- **The spotlight is one fixed element of the site**, a rounded box at the rect of the control, with a large `box-shadow` spread as the dim. It has `pointer-events: none`. The modal popover catches each tap on the dim as an outside press. `framer-motion` moves the box from one control to the next on the `GLIDE` spring of `motion.ts`.
- **The spotlight reads the rect of its control again** on a `ResizeObserver` of the control, a window `resize`, a `visualViewport` `resize` or `scroll`, and a captured `scroll`. The ui-sdk positioner already follows the card on these same events, so the card and the spotlight stay together.
- **The motion uses transitions-dev tokens:** the card opens as the Menu dropdown (05) and fades out on `--duration-quick`. The card text and the count change as Text swap soft (34). Reduced motion keeps the fades only, through `useMotionOff`. No scrolltide item fits, and `driver.js` adds 14.8 kB for what the parts above already do.

## 1. The ui-sdk parts

**Version.** `packages/design/site/package.json:9-10` pins `@ui-sdk/core` and `@ui-sdk/react` at `0.1.0-beta.2`. The lock file has the same version (`pnpm-lock.yaml:1390`, `pnpm-lock.yaml:1393`). The design package alone declares them (`docs/adr/0035-each-ui-sdk-part-has-one-wrapper.md`, Consequences).

**How the repo uses ui-sdk now.**
- `packages/design/site/ui/sheet.tsx:8-15` wraps the ui-sdk `Drawer` as the Sheet.
- `packages/design/site/ui/README.md` names `sheet.tsx` and `pending-button.tsx` as the only two files that import `@ui-sdk`.
- `packages/design/site/ui/popover.tsx:7` imports `@base-ui/react/popover`, not ui-sdk.
- `apps/site/src/ui-sdk-rule.test.ts:37-41` fails each `@ui-sdk` import outside `packages/design/site/ui/`.
- `globals.css` declares `@layer ui-sdk;` and the site loads no `web.css` (ADR 0035, Consequences).

**Parts that fit, by need.**

| Need | Part | Source |
| --- | --- | --- |
| Card next to a control, with flip and shift | `PopoverContent` with `anchor`, `side`, `align`, `sideOffset`, `collisionPadding` | `UI/docs/popups.md:7-37`; `UI/docs/components/popover.md:547-549`, `:1342` |
| Open with no trigger | `createPopoverController()` and `open({ anchor })`, or a controlled `open` | `UI/docs/components/popover.md:956-960`, `:1310` |
| Portal and z-index | None needed. Popups use the browser top layer | `UI/docs/popups.md:5` |
| Real controls do not respond | `modal` (`true`): the page is inert and scroll locks | `UI/docs/components/popover.md:614-620`, `:1314` |
| Focus trap | The same `modal`: Tab wraps inside the card | `UI/docs/popups.md:79` |
| Tap on the dim goes next | `dismissible={false}` and `onDismissAttempt`, reason `outside-press` | `UI/docs/popups.md:41-52`; `UI/docs/components/popover.md:1318-1319`, `:1414-1419` |
| Escape and Android Back | Reasons `escape-key` and `back` reach `onDismissAttempt` | `UI/docs/components/popover.md:1416-1418` |
| Focus on open | A touch open focuses the content, so no keyboard opens | `UI/docs/popups.md:66-77` |
| Focus after the Tour | Focus goes back to the element focused before | `UI/docs/popups.md:81` |
| Exit animation and done signal | `data-starting-style`, `data-ending-style`, `onOpenChangeComplete` | `UI/docs/components/popover.md:1103-1105`; `UI/docs/popups.md:87` |
| Card scale from the control | `--transform-origin`, `data-side` | `UI/docs/components/popover.md:1253-1262` |
| Title and line | `PopoverTitle`, `PopoverDescription` | `UI/docs/components/popover.md:1352-1358` |

**Do not use.**
- `presentation="auto"` turns the popover into a sheet on a small touch screen (`UI/docs/components/popover.md:1149`). Keep the default popover.
- `@ui-sdk/core` `position()` places a popup beside an anchor, not over it (`CORE/dist/foundation/platform/position.d.ts:137-152`). It cannot draw the spotlight box.
- `bindLayer` with `topLayer` joins the stack of popups (`CORE/dist/foundation/platform/bind-layer.d.ts`). A second layer for the dim would take the outside press from the card. The dim needs no layer.

## 2. The transitions

The site keeps the tokens in seconds in `apps/site/src/app/front-door/motion.ts:34-39` and `SMOOTH` at `motion.ts:8`. Use those values. Do not paste a second token block.

| Motion | Transition | Tokens | Source |
| --- | --- | --- | --- |
| Card in | Menu dropdown (05): it grows from its anchor | `--dropdown-open-dur` 250 ms (`FAST`), `--dropdown-pre-scale` 0.97, `--ease-smooth-out` | `~/.claude/skills/transitions-dev/05-menu-dropdown.md:5`, `:27-31` |
| Card out on Done or Skip | Menu dropdown close | `--dropdown-close-dur` 150 ms (`QUICK`), `--dropdown-closing-scale` 0.99 | same file `:28`, `:30` |
| Spotlight move to the next control | Position change: Tooltip (17) shows the travel of one surface between targets | `--tt-move-dur` 160 ms on `--ease-smooth-out`; the site spring `GLIDE` for a long move on a phone | `17-tooltip.md:5`, `:37-38`; `motion.ts:13-15` |
| Spotlight size change | Card resize (01) | `--resize-dur` 300 ms, `--resize-ease` smooth-out | `01-card-resize.md:21-22` |
| Card line and "2 of 4" | Text swap soft (34): a cross-blur in place, with no move | `--text-soft-dur` 200 ms, `--text-soft-blur` 2px, `--text-soft-resize-dur` 240 ms | `34-text-swap-soft.md:31-35` |
| Dim in and out | A plain fade | `--duration-fast` in, `--duration-quick` out | transitions-dev `SKILL.md`, Motion tokens |

The card stays mounted from Stop 1 to Stop 4, so the move between Stops is a move and a text swap, not an exit and an entry. This matches the rule "one surface travels" of the Tooltip. The Morph Navbar of the front door already uses this idea (`motion.ts:17-19`).

## 3. Scrolltide

Searches of `search_library` only: `tour`, `spotlight`, `onboarding`, `coach`, `walkthrough`, `tooltip`, `highlight`, `popover`. No prompt was fetched.

| Slug | Why it does not fit |
| --- | --- |
| `spotlight-carousel` | A photo rail. "Spotlight" names the wide middle card, not a dim with a hole. |
| `twilight` | A hero with a "floating tour card". It is a static card, not a set of Stops on real controls. |
| `zephyr` | A hero with a "four-step onboarding rail". It is a row of text, with no spotlight. |
| `valmora` | A camera that tours a car on scroll. No UI tour. |
| `contour-reveal` | A WebGL slideshow transition. |
| `commerce-analytics`, `property-portfolio` | Chart hover tooltips only. |
| `morph-navbar` | One shell that resizes between panels, with a gliding highlight. The idea fits the one card that travels, and `motion.ts:17` already uses it. No new item to take. |

`walkthrough` and `popover` had no match. Result: no scrolltide item shows a tour, a spotlight, or coach marks.

## 4. How the spotlight follows its control

**What ui-sdk already does for the card.** `position()` runs an animation-frame loop, and stops after 3 still frames (`CORE/dist/foundation/platform/position.js:141-142`, `:362-372`). A 500 ms timer checks again (`position.js:374`). `watchMoves` wakes it on these signals (`CORE/dist/foundation/platform/moves.js:15-49`, `:104-121`):
- a captured `scroll`, `load`, `input`, `pointermove`, `focusin`, `transitionstart`, `animationstart` on the document;
- `resize` of the window, and `resize` and `scroll` of `visualViewport`, for a pinch zoom;
- a `MutationObserver` on the whole document, and a `ResizeObserver` on the popup.

The anchor rect is read again on each check (`UI/docs/components/popover.md:1342`). The card reads the visible viewport from `visualViewport` (`position.js:180-188`).

**What the spotlight needs.** `CORE` exports no `watchMoves` (`CORE/dist/index.d.ts`), so the spotlight listens itself:
- `ResizeObserver` on the control, for a change of its size ([MDN ResizeObserver](https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver)).
- `resize` of the window. A turn of the phone fires it, because the layout viewport changes size.
- `resize` and `scroll` of `window.visualViewport`, for the keyboard and a zoom ([MDN VisualViewport](https://developer.mozilla.org/en-US/docs/Web/API/VisualViewport)).
- a captured `scroll`, because a scroll in a panel does not bubble.
- one `requestAnimationFrame` per change, so a burst gives one read.

`driver.js` uses the same set less `visualViewport` (`packages/driver/src/interaction/events.ts:141-159` in its repo). One more option is `bindViewport(el, { onChange })` of `@ui-sdk/core` (`CORE/dist/foundation/platform/viewport.d.ts:35-37`). It reports the keyboard height, the inset, and the visual viewport in one state.

**The keyboard lift.** The front door raises its ask box with `useKeyboardField` and `useKeyboardRaised` (`packages/design/site/shell/keyboard.ts:39-80`). They read `visualViewport` `resize` and `scroll` and the window `resize` (`keyboard.ts:67-71`). A raise pins the dock (`apps/site/src/app/front-door/front-door.tsx:168`, `:565`). The Drawer lifts its own content by `--keyboard-inset` (`apps/site/src/app/front-door/passphrase-sheet.tsx:40-42`). The Tour opens no field, and a touch open of the card focuses the card itself (`UI/docs/popups.md:73`). So no keyboard opens during the Tour. If a field has focus when the Tour starts, blur it first and wait for `data-keyboard` to leave the root (`keyboard.ts:19`).

**Scroll.** A modal popover locks scroll (`UI/docs/components/popover.md:620`). Scroll each control into view before its Stop opens, then measure. The prototype must check that this works under the lock.

**CSS anchor positioning.** caniuse lists full support only from Safari 27 and iOS Safari 27.0, and partial support in Chrome 125 and later and Firefox 147 and later ([caniuse](https://caniuse.com/css-anchor-positioning)). WebKit added it in Safari 26.0 ([WebKit blog](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/)). A league mate on iOS 18 gets no support. Do not use it. The JS measure works in each browser.

## 5. How the Tour sits with the other layers

**The layers now.**
- The Sheet backdrop is a popover in the top layer at `z-50` (`packages/design/site/ui/sheet.tsx:27-37`).
- The top band is `sticky z-40` (`packages/design/site/shell/top-band.tsx:35`). The dock and the Thread header are `z-10` (`front-door.tsx:435`, `:565`).
- The egg find card and end card are `fixed z-50` with `role="dialog"` (`packages/eggs/site/hunt/find-card.tsx:67`, `end-card.tsx:118`).
- The card of the Tour is in the top layer, so it sits above each of these. The spotlight must be above the band and below the card: a fixed element at `z-50` or more does this.

**Order rules for the spec.**
1. Start the Tour only when `sheetOpen` is false and `passStep` is null (`front-door.tsx:204`, `:599-611`).
2. Start it after the team sheet has gone. `TeamSheet` calls `onPick` from `onOpenChangeComplete`, after its exit (`apps/site/src/app/front-door/team-sheet.tsx:55-60`, `:62-67`). So the parent state is safe to read then.
3. The menu sheet cannot open, because the menu button is inert under the modal card (`packages/design/site/shell/menu-sheet.tsx:100-104`).
4. A Topic tap cannot open the passphrase sheet during the Tour, because the Suggestions are inert.

**The eggs.** The egg listener reads `pointerdown`, `pointerup`, `contextmenu`, and `selectionchange` on the document (`packages/eggs/site/listener/listener.ts:239-244`). It acts only on an element with `data-stable-id` (`listener.ts:94`; `packages/design/site/lib/stable-id.ts:9`). Give the spotlight and the card no `data-stable-id`. Then a tap or a hold in the Tour sends no egg check.

**Targets.** Each target has a name now: `aria-label="Suggestions"` (`suggestions.tsx:82`), the form `aria-label="Ask"` (`ask-box.tsx:25`), the team switch (`front-door.tsx:365-369`), the menu button (`menu-sheet.tsx:103`), and the pill bar `nav aria-label="Site menu"` (`packages/design/site/shell/pill-bar.tsx:19`). The pill bar shows only at `desktop:` and the menu button hides at `desktop:` (`menu-sheet.tsx:105`). Pick the Stop 4 target by which one is visible.

**Reduced motion.** `useMotionOff` reads the media query through `useReducedMotion` of `framer-motion` (`packages/design/site/hooks/use-motion-off.ts`). The front door keeps each fade and drops each move, blur, and spring (`motion.ts:3`). For the Tour: the spotlight jumps to the next control, the card fades, and the text swaps with no blur. Decision 04 sets the rest.

## 6. driver.js as a baseline

- **Version and license:** 1.14.0, released 2026-11-13, MIT (GitHub API of `kamranahmedse/driver.js`; `packages/driver/package.json` lines 3 and 5).
- **Size:** 45.9 kB minified, 14.8 kB minified and gzipped ([bundlephobia](https://bundlephobia.com/package/driver.js)). No dependencies ([repo README](https://github.com/kamranahmedse/driver.js)).
- **Spotlight:** one full-screen SVG with `fill-rule: evenodd`. Its path is the viewport plus a hole per element (`packages/driver/src/overlay/stage.ts:19-33`, `:80-89`).
- **Follow:** window `resize`, captured `scroll`, and a `ResizeObserver` on the active element (`packages/driver/src/interaction/events.ts:141-159`). It has no `visualViewport` listener, so the iOS keyboard and a zoom do not move the hole.
- **Mobile:** the README does not mention touch or mobile.
- **Why not:** it brings its own popover, focus, and keys, which repeat the ui-sdk Popover. Its CSS fights the site look of ADR 0024. Use it as a reference for the evenodd SVG only, if the box-shadow dim fails.

## Open points for the prototype (ticket 02)

1. Check that `scrollIntoView` moves the page while the modal popover locks scroll, on iPhone WebKit 390x660.
2. Check that a tap on the dim gives `onDismissAttempt` with `outside-press`, and that it does not reach the control in the hole.
3. Compare the `box-shadow` spread dim with an evenodd SVG dim: the round corners, the dark theme, and the frame rate of the move.
4. Check that the egg listener sends no check for a hold on the dim or the card.
5. Test the four viewports of `iphone-real-viewport` with an overlap assert: the card must not cover its own control.
