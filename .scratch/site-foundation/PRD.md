# Site foundation: tiers, the page column, and the menu

Status: ready-for-agent
Date: 2026-10-27

This is the first of three features that make the site responsive at every width. It sets the
tiers and the page column, and it adds the menu to the masthead. The weekly report per tier and
the other pages per tier follow as their own features. The terms come from `GLOSSARY.md`. The
house rule change is `docs/adr/0006-report-look-at-every-width.md`.

## Problem Statement

A league member opens the site on a laptop and gets a phone page: one 480px column with empty
space on both sides. The site has no navigation beyond the brand link. A reader on week 4 who
wants week 7 goes to the home page first. A reader at chapter six of the report has no way to
another page without a scroll to the top. The rankings page and the analyzer page reach only the
home page.

## Solution

The site designs for three tiers: phone, tablet, and desktop. The page column widens per tier and
the masthead spans the viewport. A menu in the masthead reaches every page: the home page, this
week's report, the power rankings, the trade analyzer, and every past week. On a phone and a tablet
a menu button opens the menu as a sheet under the masthead. On a desktop the masthead shows the
destinations as a row, with the past weeks in a popover. Once the masthead scrolls out, a compact
bar with the brand mark and the menu takes its place at the top of the viewport. The site keeps
the report's look at every tier.

## User Stories

1. As a league member on a laptop, I want the page to use the width of my screen, so that the site does not look like a phone page.
2. As a league member on a tablet, I want a page column wider than a phone's, so that the tables and the chapters read at a comfortable measure.
3. As a league member on a phone, I want the page to fill the width with the gutter it has today, so that nothing changes for the worse on the device I use most.
4. As a league member on a phone, I want a menu button in the masthead, so that I can reach any page from any page.
5. As a league member on a phone, I want the menu button at the right end of the brand line, so that my thumb finds it where every app puts it.
6. As a league member on a phone, I want the menu to open as a sheet under the masthead over a dimmed page, so that I know where it came from and that the page waits.
7. As a league member on a tablet, I want the same menu button and sheet as the phone, so that I learn one menu.
8. As a league member on a desktop, I want the destinations as a row in the masthead, so that I reach a page in one click with no menu to open.
9. As a league member on a desktop, I want the past weeks in a popover from a "Past weeks" trigger, so that the row stays short as the season grows.
10. As a league member, I want the menu to list Home, this week's report, Power rankings, and Trade analyzer in that order, so that the most read page comes first after home.
11. As a league member, I want this week's report item to carry its week number, so that I know which week is current.
12. As a league member, I want the past weeks listed newest first under a "Past weeks" heading, so that the week I most likely want is at the top.
13. As a league member, I want the item for the page I am on marked with the red accent, so that I know where I am.
14. As a league member who uses a screen reader, I want the open page's item to carry the current-page state, so that the reader tells me where I am.
15. As a league member, I want the menu to close when I choose an item, so that the new page opens with no menu over it.
16. As a league member, I want the menu to close on a tap outside the sheet, so that I can back out with one tap.
17. As a league member with a keyboard, I want Escape to close the menu, so that I can back out with one key.
18. As a league member with a keyboard, I want focus to return to the menu button when the menu closes, so that I do not lose my place.
19. As a league member with a keyboard, I want focus to stay inside the open menu, so that Tab never lands on the dimmed page.
20. As a league member who uses a screen reader, I want the menu button to say whether the menu is open and which list it controls, so that the state is spoken.
21. As a league member who uses a screen reader, I want the menu to be a labeled navigation landmark, so that I can jump to it.
22. As a league member, I want the menu button icon to morph from three lines to a cross when the menu opens, so that the button shows the state.
23. As a league member, I want the menu button to press down under my finger, so that I know the site heard the tap.
24. As a league member, I want the sheet to drop in with a short fade and leave along the same path, so that the menu feels anchored to the masthead.
25. As a league member, I want the sheet to close faster than it opens, so that a back-out feels instant.
26. As a league member, I want the menu items to arrive one after another, so that the list feels placed and not pasted.
27. As a league member who asks the system for reduced motion, I want the sheet to cross-fade with nothing that moves, so that the menu does not make me ill.
28. As a league member who asks the system for reduced motion, I want the menu button icon to switch with no morph, so that nothing moves.
29. As a league member on a desktop, I want the row links to take the red accent on hover, so that I know which link I am about to click.
30. As a league member on a touch device, I want no hover color to stick after a tap, so that a tapped link does not look chosen.
31. As a league member on a desktop, I want the Past weeks popover to scale in from its trigger, so that the list reads as part of the trigger.
32. As a league member on a desktop, I want the Past weeks popover to close on Escape and on a click outside, so that it behaves as every popover does.
33. As a league member at chapter six of the report, I want a compact bar at the top of the viewport with the menu, so that I can leave the page from where I am.
34. As a league member on a phone, I want the compact bar to show the brand mark and the menu button, so that the bar is the masthead in small.
35. As a league member on a desktop, I want the compact bar to show the brand mark and the same row as the masthead, so that I never learn two menus.
36. As a league member, I want the compact bar to slide in once the masthead scrolls out and to leave once the masthead returns, so that the bar never covers the masthead.
37. As a league member, I want the compact bar to take the black of the masthead, so that it reads as the same chrome.
38. As a league member, I want the brand mark in the compact bar to link home, so that the bar gives me the home link the masthead gives.
39. As a league member, I want the masthead to span the viewport at every tier with its content aligned to the page column, so that the black band reads as the top of the report.
40. As a league member on a desktop, I want the brand on the left and the row on the right of one line, with the week line under the brand, so that the week stays the headline.
41. As a league member, I want the week line, the title, and the subtitle in the masthead as they are today, so that each page keeps its headline.
42. As a league member, I want the home page, the rankings page, and the analyzer page to keep their content as it is, so that the foundation changes the frame and not the pages.
43. As a league member, I want the waiver page in the menu only when the league turns it on, so that a hidden page stays hidden.
44. As a league member, I want the masthead's "Waiver wire" link gone once the item lives in the menu, so that one destination shows in one place.
45. As a league member, I want every menu link to work with scripts off, so that the static page still navigates.
46. As a league member, I want the menu to list the weeks the site has published, so that a new week appears in the menu on the next publish with no code change.
47. As a league member, I want the site to look like the printed report at every tier, so that the black masthead, the red accents, and the type stay the brand.
48. As a league member on a phone, I want no sideways scroll on any page, so that the page never shifts under my thumb.
49. As a league member, I want the menu button and every menu item at least 44px tall, so that each is easy to tap.
50. As a league member, I want the link to the current page in the menu to still work, so that a tap on it closes the menu and stays put.
51. As the site's maintainer, I want the menu list built at build time from the published weeks, so that the client bundle carries no file reads.
52. As the site's maintainer, I want the masthead to stay a server component, so that the client bundle never pulls in the file system.
53. As the site's maintainer, I want one list of destinations rendered as the sheet and as the row, so that an item lives in one place.
54. As the site's maintainer, I want the tiers as named tokens, so that the report feature and the pages feature build on the same three widths.
55. As the site's maintainer, I want the page column per tier as tokens, so that a later feature tunes a width in one place.
56. As the site's maintainer, I want the old 480px tier kept until a page retires it, so that the wide tables fold as they do today.
57. As the site's maintainer, I want the motion timings in the shared motion module, so that the menu stays in tune with the site.
58. As the site's maintainer, I want the menu tests at the masthead, so that one test file covers the menu, the row, and the compact bar.
59. As the site's maintainer, I want a browser pass at 390, 768, and 1280 wide, so that the tiers get checked where jsdom cannot.

## Implementation Decisions

### Tiers and the page column

- The site designs for three tiers: phone under 640px, tablet from 640px, and desktop from
  1024px. The tiers are Tailwind's default breakpoints, named in the theme as tokens.
- The page column is a token per tier: full width with the gutter on a phone, 640px on a tablet,
  720px on a desktop. The desktop width is the content measure. The report feature adds the
  chapter rail outside it.
- The 480px tier that folds the wide tables stays until a later feature retires it.
- The masthead and the compact bar span the viewport at every tier. Their content aligns to the
  page column.

### The destinations

- One list of destinations, built at build time: Home, the current week's report labeled with its
  number, Power rankings, Trade analyzer, then the past weeks newest first under a Past weeks
  group. The waiver page joins the list only when the waiver flag is on.
- The current week is the first of the published weeks, newest first. The past weeks are the rest.
- The masthead reads the published weeks through the existing week summaries and passes the list
  to the menu as props. A test passes its own list, as the masthead's waiver link takes a value
  today.
- Each destination has a label and an href with the base path. Every link is a plain anchor, so
  the static export navigates with scripts off.
- The destination whose href matches the open page carries the current-page state and the red
  accent. The masthead learns the open page from a prop that each page passes, because a server
  component in a static export cannot read the request path.

### The menu

- The menu is a client island inside the server-rendered masthead. The masthead stays a server
  component.
- The menu renders the one list two ways: the sheet for a phone and a tablet, and the row for a
  desktop. Both exist in the DOM. The tier tokens show one and hide the other.
- The sheet builds on the site's dialog primitive, which gives the focus trap, Escape, the close on
  a tap outside, and the return of focus to the trigger. The sheet is full width under the
  masthead over a dimmed page. The page behind it does not scroll.
- The menu button sits at the right end of the brand line, 44px tall, with the expanded state and
  the controls link to the list. Its icon morphs from three lines to a cross. It takes the press
  token on pointer down.
- The list is a navigation landmark with a label. The Past weeks group has a heading.
- The desktop row shows the four page destinations as links and a Past weeks trigger. The trigger
  opens a popover on the site's component source, which the foundation adds. The popover scales in
  from its trigger and lists the past weeks newest first.
- The masthead loses its "Waiver wire" link. The waiver destination lives in the list.

### The compact bar

- The compact bar renders inside the masthead's client island, so the menu is one component with
  two places to show.
- An observer on the masthead reports when the masthead leaves the viewport. The bar slides in
  then and leaves when the masthead returns. The bar is 44px tall and takes the masthead's black.
- On a phone and a tablet the bar shows the brand mark as a home link and the menu button. On a
  desktop the bar shows the brand mark and the row.
- The bar is fixed to the top of the viewport, so it takes no space in the page flow.

### Motion

- The sheet enters with a short drop and a fade at the site's collapse timing, about 240ms, with
  the house ease-out. It exits along the same path at about 160ms. The backdrop fades with it. The
  items stagger with the site's 50ms step and its cap.
- The menu button icon morphs at about 160ms with the house ease-out.
- The popover enters at about 160ms with the house ease-out, from its trigger.
- The compact bar slides in and out with the house ease-out at the press timing.
- Only transform and opacity animate.
- The reduced-motion switch of the site turns every menu motion into a cross-fade or an instant
  switch. The sheet, the bar, and the icon move not at all with motion off.
- Hover color changes apply only on a device with a fine pointer that can hover.
- The timings join the shared motion module as named entries.

### Hover and press

- Row links take the red accent on hover, gated to a fine pointer.
- The menu button and every item take the press token, so each scales down on pointer down.

## Testing Decisions

A good test renders a component and reads what a reader sees or does: roles, names, text, and
attributes a screen reader speaks. A test never reads a class name or a style, and never asserts a
timing.

The one seam is the masthead. Its tests pass a list of weeks and an open-page href, then check:

- The menu button has a name, the expanded state, and the controls link to the list.
- A tap on the button opens the list, and the items read in order with their hrefs.
- The current week item carries its number, and the past weeks read newest first under the
  heading.
- The item for the open page carries the current-page state.
- Escape closes the list and focus returns to the button.
- A tap outside closes the list.
- The waiver item shows with the flag on and not with the flag off.
- The desktop row lists the four page links, and the Past weeks trigger opens the popover with the
  past weeks.
- A stubbed observer that reports the masthead out of view shows the compact bar, and a report
  back in view hides it.
- The masthead's "Waiver wire" link is gone.
- With motion off, the sheet and the bar render at rest. The reduced-motion test's matchMedia
  stub is the pattern.

Prior art: the masthead tests, the week chooser tests on the rankings page, and the reduced-motion
test.

What the seam cannot check gets a browser pass with agent-browser at 390 by 844, 768 by 1024, and
1280 by 800, with reduced motion on: the tier that shows per width, the page column width, no
sideways scroll, and the compact bar at a scroll position past the masthead. The rankings tickets
did the same at 390. The build and the export check run before the merge.

## Out of Scope

- The weekly report per tier, with the chapter rail. The second feature.
- The home, rankings, and analyzer pages per tier. The third feature.
- A drag to close the sheet, with velocity and a spring.
- Prior and next week links on the weekly report.
- The waiver page itself and its flag.
- Any change to the content of a page.
- Any change under the public folder.

## Further Notes

- Two choices here did not go through the grill. One: on a tablet and a desktop the body
  background and the page column background differ, so the column reads as the report's page.
  Two: each page passes its own href to the masthead, so the menu marks the open page. Brian can
  strike either.

- The house rule change is in the first ADR. The look holds at every tier; the one column drops.
- The other session publishes weeks to `main`, with a commit that stages every file. Work on the
  `site-foundation` branch, commit nothing on `main`, and rebase onto `main` before the merge.
- The glossary terms in play: menu, menu button, page column, tier, compact bar. Chapter rail is
  for the report feature.
- The design skills to load at build time: `apple-design` and `emil-design-eng` for the motion,
  `web-design-guidelines` for the accessibility pass before the merge.
