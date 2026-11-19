# 01: Which parts build the Tour

Map: `.scratch/front-door-tour/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The spec must name the parts that build the spotlight, the Stop card, and the motion between Stops. Brian prefers ui-sdk first. Use transitions.dev or a scrolltide item if one fits. `framer-motion` is fine, and the front door already uses it.

Find out:

1. Which ui-sdk parts help: a popover, a positioner, a focus trap, a dismissable layer, or an overlay. Check the version that the site uses.
2. Which transitions.dev transitions fit a Stop card and the move of a spotlight from one control to the next.
3. Which scrolltide items show a tour or a spotlight. Use search results only. Fetch no prompt.
4. How the spotlight follows its control on a resize, on a scroll, and under the keyboard lift of the Drawer.
5. How the Tour sits with the Sheet, the passphrase modal, and the easter eggs, so that no two layers fight.
6. What a tour library such as `driver.js` gives, as a baseline only.

Write the findings at `.scratch/front-door-tour/decisions/01-research-the-tour-build.notes.md`.

## Decision

The research decided it on 2026-11-18, inside the order that Brian set: ui-sdk first, then transitions.dev and `framer-motion`. The notes are at `decisions/01-research-the-tour-build.notes.md`.

1. The Stop card is the ui-sdk `Popover` of `@ui-sdk/react` 0.1.0-beta.2, with no trigger. It is `modal`, so the page is inert and focus stays in the card. It sets `presentation="popover"`, because `"auto"` turns into a sheet on a phone. An outside press goes to the next Stop, and the Escape key counts as Skip.
2. The card gets its own wrapper in `packages/design/site/ui/`, such as `stop-card.tsx`, because ADR 0035 lets only that folder import `@ui-sdk`. The name `ui/popover.tsx` is taken by the Base UI popover.
3. The spotlight is one fixed element with a large `box-shadow` dim and `pointer-events: none`. `framer-motion` moves it on the `GLIDE` spring of `motion.ts`. It measures its control again on a `ResizeObserver`, a window `resize`, a `visualViewport` `resize` or `scroll`, and a captured `scroll`. CSS anchor positioning is out, because iOS Safari support is too new.
4. The motion uses transitions-dev tokens: Menu dropdown (05) for the card entry and exit, Tooltip (17) for the move between Stops, and Text swap soft (34) for the line and the count. Under reduced motion, `useMotionOff` keeps the fades only.
5. No scrolltide item fits. `driver.js` stays a reference only, because the ui-sdk Popover covers what it gives.
6. The Tour starts only when the team sheet and the passphrase modal are closed. The dim and the card carry no `data-stable-id`, so a tap in the Tour sends no egg check. Stop 4 aims at the menu button or the pill bar, whichever one shows.
