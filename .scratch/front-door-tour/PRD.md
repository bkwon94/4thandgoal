# Front door tour: a first-visit Tour of the front door

Status: ready-for-agent
Date: 2026-11-18
Apps: site. The front door gets a Tour of four Stops, a seen key, and two replay controls. The pipeline and the API do not change.
Spec branch: `front-door-tour`.
Source: the map `.scratch/front-door-tour/MAP.md` and decision tickets 01 to 04. ADR 0035 (each ui-sdk part has one wrapper), ADR 0024 (the site look).
Tickets: 01 to 05, in `issues/`.

---

## Problem Statement

A league mate lands on the front door and sees Suggestions, an ask box, a team name, and a menu. Nothing tells them what each part does. They do not know that a Topic opens a personal answer, that the ask box takes any question about their team or their league, or that a tap on the team name shows the league as another manager. The weekly reports and the tools sit behind the menu, and many league mates never open it.

## Solution

On the first visit after the release, the front door shows a Tour. The Tour has four Stops. Each Stop dims the page, cuts a rounded hole around one real control, and shows a small card with a header, one line, a count, Skip, and Next. The hole and the card glide together from one control to the next. The last Stop says Done.

The Tour is passive: the real controls do not respond while it shows. Each browser sees it once. A "Show the tour" link in the menu sheet, and a "?" button on desktop, show it again.

## User Stories

1. As a league mate on a first visit, I want a short Tour of the front door, so that I know what each part does.
2. As a league mate on a new browser, I want the Tour to start after I pick my team, so that the Stops point at the real Suggestions of my team.
3. As a league mate who already has Your team, I want to see the Tour once after the release, so that I learn the parts that I skipped.
4. As a league mate, I want the first Stop on the Suggestions, so that I know that a Topic opens an answer for my team.
5. As a league mate, I want the second Stop on the ask box, so that I know I can type a question about my team or my league.
6. As a league mate, I want the third Stop on the team switch, so that I know I can see the league as another manager.
7. As a league mate on a phone or a tablet, I want the fourth Stop on the menu button, so that I know where every page of the league lives.
8. As a league mate on desktop, I want the fourth Stop on the pill bar, because desktop shows no menu button.
9. As a league mate, I want a count such as "2 of 4" on each Stop, so that I know how long the Tour is.
10. As a league mate, I want dots on each Stop, so that I see my place at a glance.
11. As a league mate, I want a Next button, so that I go to the next Stop when I am ready.
12. As a league mate, I want a tap on the dim area to go to the next Stop, so that a stray tap does not end the Tour.
13. As a league mate, I want a Skip button on each Stop, so that I can leave the Tour at once.
14. As a league mate, I want the Escape key to count as Skip, so that the keyboard can end the Tour.
15. As a league mate on Android, I want the Back button to count as Skip, so that Back does not leave the page.
16. As a league mate, I want the last Stop to say Done, so that I know the Tour ends there.
17. As a league mate, I want the real controls to not respond during the Tour, so that a tap in the hole does not open a Topic or a sheet by mistake.
18. As a league mate, I want the hole to sit evenly around the part of the control that I can see, so that the Stop looks exact.
19. As a league mate, I want the round menu button to get a round hole, so that the hole matches its shape.
20. As a league mate, I want the hole and the card to glide together, so that the move from one Stop to the next feels like one object.
21. As a league mate, I want the card to never cover its own control, so that I can see the control that the Stop names.
22. As a league mate, I want the card height to stay the same from Stop to Stop, so that the buttons do not jump under my thumb.
23. As a league mate, I want the page to scroll a control into view before its Stop shows, so that each Stop is on screen.
24. As a league mate who turns the phone or zooms, I want the hole and the card to follow their control, so that the Stop stays on target.
25. As a league mate with reduced motion on, I want the Tour with no glide, no blur, and no spring, so that the motion does not bother me.
26. As a league mate with reduced motion on, I want each Stop to still show, so that I get the same Tour as everyone else.
27. As a league mate in dark mode, I want the dim, the card, and the buttons to look right, so that the Tour fits the theme.
28. As a league mate, I want Next and Done in the brand accent, so that the main action is clear.
29. As a league mate who skips the Tour, I want it to not show again on its own, so that it does not nag me.
30. As a league mate who finishes the Tour, I want it to not show again on its own, so that each visit after it starts clean.
31. As a league mate who reloads during the Tour, I want it to not start again on its own, so that the reload does not trap me.
32. As a league mate on a phone or a tablet, I want a "Show the tour" link in the menu sheet, so that I can see the Tour again.
33. As a league mate on desktop, I want a "?" button beside the theme button, so that I can see the Tour again.
34. As a league mate who taps "Show the tour", I want the menu sheet to close first, so that the Tour starts on a clean page.
35. As a league mate who replays the Tour, I want it to start at Stop 1, so that I see the whole Tour.
36. As a league mate on another page, I want no replay control there, so that the shell stays the same on each page.
37. As a league mate with a screen reader, I want the card to have a title and a description, so that the reader says what the Stop is.
38. As a keyboard user, I want focus to stay inside the card during the Tour, so that Tab does not reach the dimmed page.
39. As a keyboard user, I want focus to go back to where it was after the Tour, so that I do not lose my place.
40. As a league mate on a phone, I want no keyboard to open when the Tour starts, so that the keyboard does not cover the Stop.
41. As a league mate, I want a hold or a tap during the Tour to start no easter egg, so that the Tour and the hunt do not mix.
42. As a league mate, I want the Tour to start only when no modal layer is open, such as the team sheet, the passphrase modal, or an Announcement, so that two layers never fight.
43. As a league mate in another client league, I want the same Tour, so that the copy fits a league with another menu.
44. As the commissioner, I want the Stop copy to be static, so that the Tour is the same each week and needs no build.

## Implementation Decisions

### The Stops

The four Stops, in this order, with the copy of decision 03:

| Stop | Target | Header | Line |
| --- | --- | --- | --- |
| 1 | The Suggestions | Suggestions | Picks for your team right now. Tap one to open it, or tap More for the full list. |
| 2 | The ask box | Ask | Type any question about your team or your league, such as start or sit, a trade, or the playoff race. |
| 3 | The team switch | Your team | Tap to see the league as another manager. |
| 4 | The menu button, or the pill bar on desktop | Menu | Every page of the league lives here. |

- Each target already has an accessible name: "Suggestions", the form "Ask", the team switch, the menu button, and the pill bar "Site menu". The Tour finds each target by that name, not by a new hook.
- Stop 4 aims at whichever one of the menu button and the pill bar is visible.
- The copy follows the site rules: "manager", never "rival", and no internal names.

### The parts

- **The Stop card** is the ui-sdk `Popover` of `@ui-sdk/react` 0.1.0-beta.2, with no trigger. It is `modal`, `dismissible={false}`, and `presentation="popover"`. The modal makes the page inert, locks scroll, and traps focus. `"auto"` is out, because it turns into a sheet on a phone.
- The card gets its own wrapper in the design package `ui` folder, named `stop-card`. ADR 0035 lets only that folder import `@ui-sdk`. The name `popover` is taken by the Base UI popover. The `ui` README lists the new wrapper.
- **The card places itself.** The ui-sdk positioner does not place it, because the positioner lagged the glide by up to 181 px in the prototype. The ui-sdk Popover still owns the modal, the focus, and the dismiss.
- `onDismissAttempt` maps each reason: `outside-press` goes to the next Stop, or ends the Tour on Stop 4. `escape-key` and `back` count as Skip.
- The card uses `PopoverTitle` for the header and `PopoverDescription` for the line.
- The card has role `dialog` and carries `aria-modal="true"` while the Tour shows. Another front door layer that skips when an `[aria-modal="true"]` element is open, such as an Announcement, then skips under the Tour.
- **The spotlight** is one fixed element above the top band and below the card, with `pointer-events: none`. Its large `box-shadow` spread is the dim. An SVG dim gave no gain in the prototype.
- The Tour itself is one front door part, `tour`. It owns the Stop order, the current Stop, the measure of each target, and the start rules. The shell names no Tour.

### The look

Brian chose look A, Spotlight glide, in decision 02.

- **The hole** sits on the visual box of the control, not the hit box. A control with its own fill, border, or shadow counts whole. A plain control counts only what shows, such as the menu icon.
- The pad is equal on all sides: 6 px, or 10 px for a box under 28 px tall.
- The round menu button gets a circle. Each other control gets a pill.
- **The card** has a header line: the name of the control on the left, and "1 of 4" on the right. Under it sit the line, the dots, Skip, and Next or Done.
- The card height never changes. The line box holds all four lines in one grid cell, so the tallest line sets the height.
- Next and Done use `bg-accent text-on-dark` in both themes, as the send button and the passphrase submit do.

### The motion

The motion uses the transitions-dev tokens that `motion.ts` already holds. It adds no second token block.

- The dim fades in on `FAST` and out on `QUICK`.
- The card opens as Menu dropdown (05): it grows from 0.97 on `FAST` with the smooth-out ease. It closes on `QUICK` at 0.99.
- The hole and the card move between Stops on the same `GLIDE` spring, so the two never part. The card stays mounted from Stop 1 to Stop 4.
- When the card changes side of its control, it fades out, holds its place, and fades back in once the hole lands.
- The header, the line, and the count change as Text swap soft (34).
- On a move that scrolls the page, the scroll ends first. Then the Tour measures the target, and the hole and the card glide. This removes the 5.1 px drift of one frame that the prototype showed.

### Reduced motion (decision 04)

The Tour reads `useMotionOff`, as the other front door parts do. Under reduced motion:

- Each Stop still shows, with the same copy and the same controls.
- The hole jumps to the next control. It does not glide.
- The card fades out at the old Stop and fades in at the new one. It does not glide and does not scale.
- The header, the line, and the count swap by opacity only, with no blur.
- The dim keeps its fade in and its fade out.
- A scroll into view uses no smooth scroll.

### Follow the control

- The Tour measures the target again on a `ResizeObserver` of the target, a window `resize`, a `visualViewport` `resize` or `scroll`, and a captured `scroll`.
- One `requestAnimationFrame` per change gives one read for a burst of events.
- CSS anchor positioning is out, because iOS 18 Safari does not support it.
- Before each Stop, the Tour scrolls its target into view. The prototype showed that this works under the scroll lock of the modal card on iPhone WebKit.

### The start rules

- The Tour starts only when no `[aria-modal="true"]` element is open. This covers the team sheet, the passphrase modal, and an Announcement.
- If a modal layer is open, the Tour waits. It starts after the last modal layer finishes its exit.
- On a new browser, the Tour starts after the team sheet finishes its exit. The team sheet calls its pick from `onOpenChangeComplete`, so the Suggestions of Your team are on the page.
- If a field has focus when the Tour starts, the Tour blurs it and waits for the keyboard lift to end.
- The spotlight and the card carry no `data-stable-id`, so a tap or a hold in the Tour sends no egg check.

### The seen key (decision 04)

- The key is `cpc.tour-seen` in `localStorage`. It sits beside `cpc.opened-topics`, `cpc.thread`, and the key of Your team, and it follows their `cpc.` prefix. It has its own key, so the Tour never mixes with the other stores.
- The value is `"1"`. Any value counts as seen.
- The Tour writes the key when Stop 1 opens. So Done, Skip, and a reload during the Tour each count as seen.
- No browser has the key at the release, so each browser sees the Tour once, with or without Your team.
- A replay does not read the key, and it writes it again.
- If the read of `localStorage` throws, the Tour counts as seen and does not start. A blocked store then gives no Tour on each visit.
- The seen store is one small module beside the opened store and the Thread store, with the same shape: one read and one write.

### The replay (decision 03)

- On a phone and a tablet, the menu sheet shows a "Show the tour" link. The front door passes it into the menu sheet through a slot, so the shell names no Tour.
- On desktop, a "?" icon button sits beside the theme button, through the `actions` slot of `TopBand`. Its accessible name is "Show the tour".
- Both show only on the front door.
- A tap on either one closes the menu sheet if it is open. After the sheet finishes its exit, the Tour starts at Stop 1.
- The pill bar gets no Tour item, because it holds only page links. Stop 4 gives no replay hint.

## Testing Decisions

A good test checks what a league mate sees and does: which Stop shows, where the hole and the card sit, what a tap does, and what the browser stores. It does not check the inner state of the Tour or the props of the ui-sdk Popover.

### The seams

1. **The Playwright seam on the static export.** This is the main seam. The front door e2e specs serve `out/` of the current client and drive the real page. Prior art: `front-door.spec.ts`, `front-door-reduced.spec.ts`, `front-door-glide.spec.ts`, and the helpers in `door-motion.ts`. The Tour tests cover:
   - the start on a new browser after the team pick, and the start on a browser that already has Your team;
   - Next, a tap on the dim, Skip, Escape, and Done;
   - the seen key, a reload, and no Tour on the second visit;
   - the replay from the menu sheet and from the "?" button;
   - a tap in the hole that opens nothing;
   - the overlap assert on the four viewports of the iPhone rule: 390x660 iPhone WebKit, iPad 810x980 and 1080x740, and 1280x800 desktop. The card must not cover its own control.
   - the hole and the card that stay together during a glide, by samples, as `front-door-glide.spec.ts` does;
   - reduced motion: no move of the hole between samples, and opacity-only swaps, as `front-door-reduced.spec.ts` does;
   - no egg check for a hold on the dim or the card, as `eggs.spec.ts` does;
   - both themes.
2. **The Vitest seam on the components.** The Tour and the seen store get component and unit tests with Testing Library, as `suggestions.test.tsx`, `team-sheet.test.tsx`, and `passphrase-sheet.test.tsx` do. They cover the Stop order, the copy, the count, the Stop 4 target choice, the reason map of `onDismissAttempt`, the start rules, and the seen key, with the throw case.
3. **The ui-sdk rule test** already fails each `@ui-sdk` import outside the design `ui` folder. The `stop-card` wrapper must pass it. No new test.

Brian checks these seams with this spec.

## Out of Scope

- A Tour on the other pages. The front door is where a league mate lands, and the menu Stop points at the other pages.
- Live facts of the week in the Stops. Static copy keeps the Tour the same from week to week.
- A replay link on the other pages. It needs a signal through the URL, and the shell then knows the Tour. Home is one tap away.
- Any pipeline or API change. The Tour needs only data that the front door already has.
- A Stop inside the menu sheet. The menu sheet does not open during the Tour.
- A tour library such as `driver.js`. The ui-sdk Popover already gives the modal, the focus, and the dismiss.

## Further Notes

- The prototype is on the local branch `front-door-tour-proto`, at `af82b8ef` and `ee3b8111`. It never touched the Spec branch. It is a reference for the hole pad, the side change of the card, and the glide samples. Delete the branch after the spec merges.
- Each UI ticket uses the design bar: `transitions-dev`, scrolltide, `apple-design`, `animate`, `critique`, and `polish`.
- The glossary already holds "Tour" and "Stop". No new term and no ADR.
