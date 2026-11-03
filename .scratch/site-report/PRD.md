# Site report: the weekly report per tier

Status: ready-for-agent
Date: 2026-10-27

This is the second of three features that make the site responsive at every width. The
foundation, `.scratch/site-foundation/`, set the tiers, the page column, and the menu. This
feature designs the weekly report for a tablet and a desktop, adds the chapter rail, and adds the
week footer. The home, rankings, and analyzer pages per tier follow as the third feature. The
terms come from `GLOSSARY.md`. The house rule is `docs/adr/0006-report-look-at-every-width.md`.

## Problem Statement

A league member opens the weekly report on a laptop and gets the phone design stretched to 720px.
The body text runs about 95 characters per line, past a comfortable measure. The game changer
hero has its cutout stuck at the right edge with empty space beside the points. The awards, the
leaders, the trades, and the next week cards stack in one column with the width unused. A reader
at chapter six has no way to the standings except a scroll. A reader at the end of week 6 has no
link to week 7.

## Solution

From the tablet tier up each chapter gets a composition for the width: the hero puts the text on
the left and the cutout on the right, the card chapters go to two or three columns, and the tables
and the chart use the room. The type scale steps up one size per tier and the blurbs cap at a
comfortable measure. Each chapter is a white or dark card on the grey body. On a desktop a chapter
rail sits left of the column, lists the nine chapters, and marks the one in view. The report ends
with a week footer that links the prior and the next week. The phone keeps the report as printed.

## User Stories

1. As a league member on a laptop, I want each chapter to use the width of the column, so that the report reads as a page designed for my screen.
2. As a league member on a tablet, I want the same compositions as a laptop where they fit, so that a tablet is not a big phone.
3. As a league member on a phone, I want the report as it is today, so that the device I read on most does not change.
4. As a league member, I want the body text no wider than about 68 characters, so that my eye finds the next line.
5. As a league member on a laptop, I want the type one size larger than on a phone, so that I read at a normal distance from a big screen.
6. As a league member on a tablet, I want the type between the phone size and the laptop size, so that the step feels even.
7. As a league member on a laptop, I want the week line, the scores, and the points to grow with the type, so that the headline stays the headline.
8. As a league member on a tablet or a laptop, I want the game changer's name and points on the left and the cutout on the right, so that the hero reads as one picture.
9. As a league member, I want the hero at a set height from the tablet tier up, so that a long name or a short one gives the same hero.
10. As a league member, I want the hero blurb under both halves at the capped measure, so that the story reads after the picture.
11. As a league member on a phone, I want the hero as it is, so that the phone hero stays the top story.
12. As a league member on a tablet or a laptop, I want three award tiles per row, so that the six awards sit in two rows.
13. As a league member on a tablet or a laptop, I want two position leader cards per row, so that the positions pair up.
14. As a league member on a tablet or a laptop, I want two trade cards per row, so that two trades compare side by side.
15. As a league member on a tablet, I want two next week cards per row, and three on a laptop, so that the slate fits the width.
16. As a league member on a laptop, I want the matchup of the week score row to use the width, so that the two teams and the score sit apart.
17. As a league member on a laptop, I want the all matchups rows to use the width, so that the names never wrap.
18. As a league member, I want the recap to open inline under its row at every tier, so that one tap does the same thing everywhere.
19. As a league member on a laptop, I want the median chart to use the width, so that each bar is readable.
20. As a league member on a laptop, I want the standings rows to use the width, so that the rank, the record, and the points sit apart.
21. As a league member on a tablet or a laptop, I want each chapter as a card on the grey body with an even gap, so that the chapters read as placed, not stacked.
22. As a league member, I want the dark chapters, the hero and the standings, as dark cards, so that they keep their look.
23. As a league member on a phone, I want the unbroken white page with the chapter rules, so that the phone report stays as printed.
24. As a league member on a laptop, I want a chapter rail left of the column, so that I see the whole report at a glance.
25. As a league member on a laptop, I want the rail to list the nine chapters in the report's order, so that the rail is the report's table of contents.
26. As a league member on a laptop, I want the chapter in view marked in red in the rail, so that I know where I am.
27. As a league member on a laptop, I want a tap on a rail label to scroll to that chapter, so that I reach the standings in one tap.
28. As a league member on a laptop, I want the rail to stay in view under the compact bar as I scroll, so that it is always at hand.
29. As a league member with a keyboard, I want each rail label as a link I can reach with Tab, so that I jump with Enter.
30. As a league member who uses a screen reader, I want the rail as a labeled navigation landmark, so that I can jump to it or skip it.
31. As a league member who uses a screen reader, I want the in-view chapter's label to carry the current state, so that the reader tells me where I am.
32. As a league member who asks for reduced motion, I want a rail tap to jump with no smooth scroll, so that the page does not slide.
33. As a league member on a tablet or a phone, I want no rail, so that the column keeps the width and the menu does the jump.
34. As a league member at the end of the report, I want a link to the prior week on the left, so that I read back through the season.
35. As a league member at the end of the report, I want a link to the next week on the right when it exists, so that I read forward.
36. As a league member, I want each footer link to show the week number and its dates, so that I know what I open.
37. As a league member, I want a missing prior or next week to leave its slot empty, so that the row keeps its shape.
38. As a league member, I want the footer links to press down under my finger, so that they feel like the home rows.
39. As a league member, I want the footer to appear on week 6 pointing at week 7 after the week 7 publish, so that no code change is needed per week.
40. As a league member, I want every link in the rail and the footer as a plain anchor, so that the static page navigates with scripts off.
41. As a league member, I want no sideways scroll at any width, so that the page never shifts under my thumb.
42. As a league member, I want the reveal of each chapter as it is, so that the report still arrives as I scroll.
43. As a league member, I want the report to look like the printed report at every tier, so that the black masthead, the red accents, and the type stay the brand.
44. As the site's maintainer, I want the type scale per tier as tokens, so that one place sets the sizes.
45. As the site's maintainer, I want the hero height, the rail width, the card gap, and the measure as tokens, so that a later feature tunes them in one place.
46. As the site's maintainer, I want the rail as one client island in the server page, so that the page stays a server component.
47. As the site's maintainer, I want the chapter ids as the one source for the rail's anchors, so that a renamed chapter cannot break a link.
48. As the site's maintainer, I want the week footer to read the published week summaries at build time, so that the client bundle carries no file reads.
49. As the site's maintainer, I want the tests at the week page, so that one test file covers the rail, the footer, and the chapter order.
50. As the site's maintainer, I want a browser pass at 390, 768, and 1280 with a screenshot per chapter, so that each composition is checked where jsdom cannot.

## Implementation Decisions

### The type scale and the measure

- The type scale tokens, label through headline and the hero number, carry one value per tier. The body is 14px on a phone, 15px on a tablet, and 16px on a desktop. The other sizes step the same way, with the ratio of the print scale kept. The tier variants on the root switch the tokens, as the page column does today.
- The measure is a token of about 68 characters. Every blurb, the matchup recap, and the hero blurb take it as a max width. Tables, grids, and score rows do not.
- The line height follows the print scale per size.

### Chapters as cards

- From the tablet tier up, each chapter takes the page column's white, or its own dark, with a token gap between chapters, so the chapters read as cards on the grey body. The chapter rule between chapters goes away at those tiers. On a phone the chapters stay one unbroken page with the rules.
- The card edge is square, as the printed report is. No shadow, no radius.

### Compositions from the tablet tier up

- The game changer hero: a two-part composition at a token height. The left part holds the label, the name, the position line, the points, and the projected line. The right part holds the cutout on the red glow, bottom-aligned, clipped to the hero. The blurb runs under both parts at the measure. The three reveal parts, the glow, the cutout, and the points, keep their delays.
- The awards: three tiles per row from the tablet tier. Two on a phone.
- The position leaders: two cards per row from the tablet tier. One on a phone.
- The trades: two cards per row from the tablet tier. One on a phone. A trade card keeps its two inner columns.
- The next week: two cards per row on a tablet, three on a desktop. One on a phone.
- The matchup of the week: the score row spreads the two teams to the edges with the score centered. The blurb takes the measure.
- The all matchups: the rows use the width, the names never wrap, and the recap opens inline under its row at every tier, as today.
- The median game: the three KPI cells and the chart use the width. The bars keep their order and the dashed median line.
- The standings: the rows use the width with the columns spaced by tokens. No new columns, because the data has only the rank, the record, and the points.
- The 480px tier that folds the wide tables stays for a phone.

### The chapter rail

- A client island rendered by the week page on every tier and shown from the rail tier by the tier variant. The rail tier is 1152px, where the margin beside the 720px column holds the rail plus the gap: 720 + 2 × (180 + 24) = 1128. It takes the list of chapters, each with an id and a label, from the page at build time. The chapter ids are the ones the chapter parts already set.
- The rail sits left of the page column, outside it, at a token width of about 180px, sticky under the compact bar. The column keeps its 720px measure.
- The rail is a navigation landmark with a label. Each label is a plain anchor to the chapter id, in the report's label style, muted ink, the in-view chapter in red with the current state.
- An observer on the chapters marks the one nearest the top of the viewport as in view. The mark is state in the island.
- A tap scrolls to the chapter. With reduced motion the scroll is instant; otherwise the page's scroll behavior applies. The compact bar's scroll padding keeps the chapter's label clear of the bar.
- Under the rail tier the rail is hidden and the column stays centered. On a phone the page is one column.

### The week footer

- A row at the end of the report, after the next week chapter, with the prior week on the left and the next week on the right. Each is a plain anchor with the base path in the home row style with the press feedback, with the week number as the lead and the dates under it.
- The page reads the published week summaries at build time and passes the prior and the next week, or null for each, to the footer. A missing side leaves its slot empty, so the other keeps its side.
- The footer reveals as the chapters do.

### Motion

- No new animation. The reveal, the stagger, and the hero delays stay as they are. The rail's in-view mark changes color through the house transition on color, with no motion when motion is off.

## Testing Decisions

A good test renders a page or a component and reads what a reader sees or a screen reader hears:
roles, names, text, hrefs, and the attributes a reader hears. A test never reads a class name, a
style, a token, or a timing.

The one seam is the week page, rendered with the real published data as the home page test does
today. Its tests check:

- The nine chapters render in the report's order with their ids.
- The rail is a navigation landmark with a label, and lists nine links in order, each to a chapter id.
- A stubbed observer that reports a chapter in view marks that link with the current state, and a report of another chapter moves the mark.
- The week footer on week 7 links to week 6 on the left and has an empty right slot. The footer on week 6 links to week 5 on the left and week 7 on the right. Each link shows the week number and its dates.
- Every rail and footer link is a plain anchor with the base path.
- With motion off, the page renders at rest.

Prior art: the home page tests with the real public data and the temp public folder, the
masthead tests with the observer stub, and the reduced-motion test.

What the seam cannot check gets a browser pass with agent-browser at 390 by 844, 768 by 1024, and
1280 by 800, with reduced motion on: a screenshot per chapter per width, the measure, the type
step per tier, the cards and the gap, the hero composition, the grid columns per tier, the rail at
1280 with the in-view mark after a scroll, no rail at 768 and 390, the footer, and no sideways
scroll. The build and the export check run before the merge.

## Out of Scope

- The home, rankings, and analyzer pages per tier. The third feature.
- New data in any chapter, such as more standings columns.
- A side panel for the recap.
- A rail on a phone or a tablet.
- Any change to the menu, the sheet, the row, or the compact bar.
- Any change under the public folder.

## Further Notes

- Branch `site-report`, off `main`. Commit nothing on `main`. Rebase onto `main` before the merge, because a week publish lands there.
- The glossary terms in play: chapter, chapter rail, tier, page column, compact bar.
- The design skills to load at build time: `emil-design-eng` and `apple-design` for the hero and the rail, `typeset` for the type scale, `web-design-guidelines` for the accessibility pass before the merge.
- Open from the foundation, outside this feature: no theme-color meta, no tap highlight color on the press utility, the masthead home link's spoken name runs the title into the subtitle.
