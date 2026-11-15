# ui-sdk sheet: the menu sheet runs on the ui-sdk Drawer

Status: ready-for-agent
Date: 2026-11-14
Apps: site. The menu sheet of the front door moves to the ui-sdk `Drawer`, and the design package gets its first ui-sdk wrapper and the rules for later moves. The pipeline does not change.
Spec branch: `ui-sdk-sheet`.
Source: the map `.scratch/ui-sdk-sheet/MAP.md` and decision tickets 01 to 10. ADR 0034, ADR 0024, and ADR 0012.
Tickets: none yet. `4ag:to-tickets` writes them.

## Problem Statement

A manager opens the menu sheet on the front door with a phone. The sheet drops from the top band, but its drag is hand-built. It follows the finger with a home-made rubber band and closes on a fixed distance or speed. It does not settle on a spring, and it does not feel like a native sheet.

The hand-built code also costs us. Each sheet of the site has its own drag, focus, and close code, and each one needs its own tests. ui-sdk gives drag, spring, snap, focus, and ARIA with no styles of its own, but nothing in the repo uses it yet. No rule says how a ui-sdk part enters the design package, so the first move must also set the rules for the next four sheets.

## Solution

The menu sheet runs on the ui-sdk `Drawer` on the live front door. It drops from the top band, follows the finger, and settles on the default iOS spring. It has one snap point at the height of its rows and a small grab handle at its bottom edge. The page under the band dims as the sheet opens, and the page does not scale. A short drag on a row still opens the row.

Under reduced motion, the sheet fades in and out and does not slide (ADR 0034). On the desktop the pill bar takes its place, as now. The dock pages do not change, and they load no `Drawer` code.

The design package gets one wrapper for the ui-sdk sheet, and no other file imports `@ui-sdk`. A rule test fails an import of `@ui-sdk` outside the wrapper folder. Tailwind styles the wrapper, and the ui-sdk default look stays out.

## User Stories

1. As a manager on a phone, I want the menu sheet to follow my finger when I drag it, so that it feels like a sheet of the phone itself.
2. As a manager on a phone, I want the sheet to settle on a spring when I let go, so that the motion feels physical and not scripted.
3. As a manager on a phone, I want a flick up to close the sheet, so that I can close it fast with one move.
4. As a manager on a phone, I want a slow drag up past its edge to close the sheet, so that a careful close works too.
5. As a manager on a phone, I want a short drag that does not reach the close to send the sheet back, so that a small slip does not close it.
6. As a manager on a phone, I want a drag down past the open place to meet more and more resistance, so that the sheet feels anchored to the band.
7. As a manager on a phone, I want a tap on a row to open its page, even if my finger moved a few pixels, so that a tap stays a tap.
8. As a manager on a phone, I want a real drag that starts on a row not to open that row, so that a drag never sends me to a page by accident.
9. As a manager on a phone, I want a small grab handle at the bottom edge of the sheet, so that I can see the sheet drags.
10. As a manager on a phone, I want the sheet to open to the height of its rows, so that all pages show at once with no second pull.
11. As a manager on a phone, I want "Past weeks" to open under the week row and push the rows under it down, so that no row gets covered.
12. As a manager on a phone, I want the page under the band to dim as the sheet opens, and to follow my drag, so that I see the sheet sits above the page.
13. As a manager on a phone, I want a tap on the dimmed page to close the sheet, so that I can close it without a search for the X.
14. As a manager on a phone, I want the menu button to turn into an X in the same spot while the sheet is open, so that the way out sits under the thumb that opened it.
15. As a manager on a phone, I want the top band and its X to stay bright and usable over the open sheet, so that the sheet seems to drop out of the band.
16. As a manager on a phone, I want each row to show its icon, its name, and its note, so that I know what each page is for.
17. As a manager on a phone, I want a check on the row of the page I am on, so that I know where I am.
18. As a manager on a phone, I want the week row to open the latest report, and "Past weeks" to list every week, newest first, so that I can reach an old week.
19. As a manager with reduced motion turned on, I want the sheet to fade in and out instead of a slide or a spring, so that the motion does not bother me.
20. As a keyboard user, I want the focus to move into the sheet when it opens, so that I start at the top of the rows.
21. As a keyboard user, I want Escape to close the sheet and put the focus back on the menu button, so that I do not lose my place.
22. As a keyboard user, I want the focus to stay in the sheet and the band while the sheet is open, so that Tab does not reach the hidden page under the dim.
23. As a screen reader user, I want the closed sheet out of the accessibility tree, so that I do not hear rows I cannot see.
24. As a screen reader user, I want the open sheet named as the pages of the site, so that I know what opened.
25. As a screen reader user, I want the menu button named "Open the menu" or "Close the menu", so that I know what it does now.
26. As a manager on a desktop, I want the pill bar in the band instead of the menu sheet, so that the pages show inline on a wide screen.
27. As a manager with scripts turned off, I want no menu button that does nothing, so that the page shows no dead control.
28. As a manager on a dock page, I want the page to load no more code than before, so that the move of the front door does not slow my page.
29. As a manager on a slow phone network, I want the first tap on the menu button to open the sheet with no wait, so that the front door feels quick.
30. As the commissioner, I want the menu sheet in the brand colors and the shared look, so that it matches the rest of the site in each league.
31. As an agent who builds a later sheet, I want one wrapper of the ui-sdk sheet in the design package, so that I reuse it and do not import ui-sdk myself.
32. As an agent who builds a later sheet, I want a rule test to fail an import of ui-sdk outside the wrapper folder, so that the rule holds without a review.
33. As an agent who builds a later sheet, I want the wrapper styled by Tailwind on the slot and state attributes, so that I follow the same pattern.
34. As an agent who bumps ui-sdk, I want both packages pinned to one exact version, so that a bump is one change that I test once.
35. As a maintainer, I want the hand-built drag code of the menu sheet removed, so that fewer lines of code need tests.
36. As a maintainer, I want the README of the wrapper folder to name the ui-sdk sheet and its rule, so that a new reader finds the rule fast.

## Implementation Decisions

- **The wrapper.** The design package gets one wrapper of the ui-sdk `Drawer`, in the folder of the shadcn primitives, as the sheet (decision 06). It exports the sheet parts that the menu sheet needs: the root, the trigger, the backdrop, the content, the handle, the title, and the close. It knows no league term. Tailwind styles each part on `data-slot`, the state attributes, and the CSS variables of the `Drawer`. No `web.css` loads. The README of the folder adds the sheet and the rule that only this folder imports `@ui-sdk`.
- **The CSS layer.** The global CSS of the site declares `@layer ui-sdk;` as its first rule, above the import of Tailwind (decisions 06 and 07). Tailwind utilities then win over the ui-sdk rules, also on the `adoptedStyleSheets` path of a later CSP.
- **The menu sheet.** It keeps its place in the shell of the design package, its rows, its notes, its check, and "Past weeks" with its grid-row growth. It drops its own drag code: the slop, the rubber band, the close distance and speed, the pointer handlers, and the click guard after a drag. The `Drawer` does each one (decision 08).
- **The feel (decision 08).** `side="top"`. One snap point, the default `"content"`. A grab handle at the bottom edge. The default `sheetPhysics.ios`, with no tune. The scrim opacity follows `--drawer-dim`. The page does not scale. Under reduced motion the sheet fades over 150 ms and does not slide (ADR 0034, decision 07).
- **The band stays on top.** The `Drawer` puts its viewport in the top layer, which covers the band. A CSS rule moves the top edge of the viewport and the backdrop to the bottom of the band. `persistentElements` keeps the band usable while the sheet is modal, so the X in the band closes it.
- **Focus.** The sheet is modal. The focus moves into the sheet on open, stays in the sheet and the band, and goes back to the menu button on a close. The old rule that a Tab out of the sheet closes it goes away, because the modal keeps the focus in.
- **Only the front door pays (decision 10).** The top band no longer imports the menu sheet. The front door gives the menu sheet to the top band, for example as a prop that takes the place of `nav="sheet"`. The top band shows that sheet in the banner, in place of the dock and the week chip. The 11 dock pages import no `Drawer` code. The front door imports the `Drawer` directly, with no lazy load.
- **The dependency (decision 09).** The `package.json` of the design package declares `@ui-sdk/react` and `@ui-sdk/core`, each pinned to one exact version, with no caret. The site app gets them through its workspace dependency on the design package, so the app does not declare them. Use the newest `0.1.0` beta at build time. Decision 07 tested `0.1.0-beta.1`. `0.1.0-beta.2` holds patches only, and none touches the `Drawer`.
- **The guard (decision 09).** A rule test beside the component rule fails an import of `@ui-sdk` in any source file outside the wrapper folder. It scans the site side of each package and the source of the site app. It uses the shared rule report, so a failure names the file, the line, the rule, and the fix: "import the wrapper in the ui folder of the design package".
- **Names (decision 04).** Prose and copy say "sheet" and "menu sheet". `Drawer` appears only in code, as a Technical Name of ui-sdk.

## Testing Decisions

A good test checks what a manager sees and does: the roles, the names, the focus, and the close. It does not check the class names, the pointer handler names, or the internals of ui-sdk.

The seams, from the highest down:

1. **The front door on the static build, in a real browser.** Playwright runs the static `out/` on a 390 x 844 phone context with touch, on a narrow desktop window, and with reduced motion. It records the drag, the spring, the snap, the handle, the dim, the close by a flick, a short drag that still taps, and the fade under reduced motion. This is the seam for the feel, because jsdom has no layout, no top layer, and no spring. Prior art: the evidence runs of decision 07 and of the front door features.
2. **The bundle sum on the static build.** The gzip sum of each script that the HTML of a page loads, as in decision 07. The sum of `/rankings/` does not grow, and the sum of `/` grows by about the cost of the `Drawer`.
3. **The top band in Testing Library.** The tests of the top band in the design package keep their behavior checks of the menu sheet: closed and out of the accessibility tree, the rows with icon, name, note, and check, the X in place of the menu button, the focus on open, the close by the X, by a tap on the dim, and by Escape, the week row, and "Past weeks". Each test that checks the hand-built drag moves to seam 1. The test of the close on a Tab out changes to a check that the focus stays in. If jsdom cannot open the `Drawer`, the agent reports it, and the check moves to seam 1. Prior art: the existing sheet tests of the top band.
4. **The rule test.** It runs the rule on one string, as the component rule does: an import of `@ui-sdk` outside the wrapper folder fails with the file and the line, and an import inside passes. Then it runs on the real tree and passes. Prior art: the component rule test and the rule report.

## Out of Scope

- The other four sheets: the player sheet, the claim sheet, the team sheet, and the passphrase sheet. Each one copies the rules in its own spec after this one ships.
- The side tabs, the show-all control, the index list, and other hand-built controls. The same reason.
- The ui-sdk default look, `web.css`. The look of ADR 0024 owns the components (decision 06).
- The pill bar of the desktop. It is no sheet, and it works.
- The dock. It is no sheet, and it works (decision 10).
- A standing check of the bundle size in CI. It is its own feature (decision 10).
- A mouse drag on a row of the sheet on the desktop. The native drag of the link stops it in the current sheet too, and touch works (decision 08).
- A sheet from the bottom edge. It lost in the prototype, because a sheet must move in from the edge of the button that opens it (decision 08).

## Further Notes

- ui-sdk is a beta, two days old on 2026-11-14, with one patch release and no API break (decision 07). The exact pin makes each bump a deliberate change.
- The prototype of decision 08 sits on the branch `ui-sdk-sheet-08-prototype` at `896e43f6`. It shows the CSS rule that keeps the band on top and the use of `persistentElements`. Do not merge that branch. Rewrite what it shows properly.
- `next dev` rewrites the AGENTS.md of the site app and `next-env.d.ts`. Restore both before a commit.
- A phone check off the home Wi-Fi uses the Tailscale IP of the Mac. Add it to `allowedDevOrigins` only for the check.
