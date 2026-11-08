# Hero slots: one hero family, with a scene of the week on top

Status: ready-for-agent
Date: 2026-11-07
Apps: site. `Hero` takes six hero slots, all 11 heroes move to them, and the first hero of a page draws a hero scene. The pipeline does not change. The scene draws data that the pipeline already publishes.
Spec branch: `hero-slots`.
Source: the map `.scratch/hero-slots/MAP.md` and decision tickets 01 to 07. ADR 0024, ADR 0025, ADR 0027.
Tickets: 01 to 10, in `issues/`.

## Problem Statement

A manager reads the site on a phone. Every page opens on a hero, but no two heroes look alike. The titles use four sizes, the eyebrows differ or are missing, and each page lays out its numbers its own way. The site feels like many small sites, not one. The hero is also meant to be the one loud part of a page (ADR 0024), but on a phone it shows only a scan line on entry and then sits still. Nothing in it says anything about the week, and nothing in it makes a manager say "wow".

## Solution

Every hero gets the same six places in the same order: an eyebrow, a title, a meta line, one feature, the stats, and an action. Each place has one style, so the heroes read as one family on every page. On a phone the places stack in one column. From the tablet width up, the hero takes a two-row layout like a broadsheet page, with the title in the top row, the stats and the action in the bottom row, and an open middle.

The first hero of a page draws a hero scene. Points of light start scattered, drift in, and settle into a small star chart of that page's real data: the 12 scores of the week, the weeks of one team, the power rank, or the two sides of a trade. One light shows its label at rest. A manager taps anywhere in the scene to read the nearest light, or slides a finger across it to read each light in turn. A small hint, "TAP OR SLIDE", shows once. The scene plays again each time the hero comes back into view.

## User Stories

1. As a manager, I want every hero on the site to share one structure, so that the site feels like one product.
2. As a manager, I want the title of every hero in the same size and weight, so that I always know where to look first.
3. As a manager, I want every hero to have the same small uppercase eyebrow, so that I always know which page or which week I am on.
4. As a manager, I want the meta line kept to one or two lines, so that the hero stays short on my phone.
5. As a manager, I want the meta line at 16px, so that a full sentence, such as the reason of a verdict, is easy to read.
6. As a manager, I want the unique part of each page, such as the team rows or my grade, always in the same place, so that I find it without a search.
7. As a manager, I want the numbers of a hero in a row of tiles at the same place on every page, so that I compare them at a glance.
8. As a manager, I want the links and buttons of a hero at its bottom, so that I always know where to tap next.
9. As a manager on a phone, I want the hero in one column, so that nothing is cramped.
10. As a manager on a tablet or a laptop, I want the hero to use the width, so that the title and the meta sit side by side and the hero is not a tall strip.
11. As a manager, I want a hero with no stats or no action to show no empty gap, so that the hero does not look broken.
12. As a manager, I want the Matchup of the Week to have a title in words, such as "The Blue Tent by 1.43", so that I know the story before I read the numbers.
13. As a manager, I want the long blurb of the Matchup of the Week under the hero, not inside it, so that the hero stays as short as the others.
14. As a manager, I want the 404 page to say "Page not found" in the same title style as every hero, with the big "404" kept as art, so that even the error page feels like the site.
15. As a manager, I want the week chips of a manager page next to the grade, so that the meta line stays short.
16. As a manager, I want the record line, such as "7-9 · 9th of 12", as the eyebrow of a manager page, so that I see the standing first.
17. As a manager, I want the first hero of a page to show a scene of real data, so that the page opens with something true and striking about the week.
18. As a manager, I want the lights of the scene to drift in and settle into a chart, so that the chart forms in front of me.
19. As a manager, I want the settle to take about two seconds, so that I can follow it but do not wait for it.
20. As a manager, I want the Matchup scene to show all 12 scores of the week with the league median, so that I see where the Matchup sits in the whole week.
21. As a manager, I want the two teams of the Matchup to flare in the brand color, so that the story of the hero stands out of the chart.
22. As a manager, I want the margin of the Matchup, such as "+1.43", always visible in the scene, so that no label hides it.
23. As a manager, I want my manager page to show my weeks as lights, bright for a win and dim for a loss, against the median, so that I see my season at a glance.
24. As a manager, I want the power rankings page to show 12 lights in the order of the power rank, each at its playoff odds, with the rank-1 team in the brand color, so that I see the race at a glance. Dropped by Brian on 2026-11-08.
25. As a manager, I want the analyzer to show drifting lights while I build a trade, so that the page feels alive before the answer. Dropped by Brian on 2026-11-08.
26. As a manager, I want the lights of the analyzer to settle into two groups when the verdict arrives, with the bigger group on the side that gets more, so that I see the answer as it lands. Dropped by Brian on 2026-11-08.
27. As a manager, I want the midseason report to open on a scene of the season totals in the order of the standings, so that the report starts with the whole season. Dropped by Brian on 2026-11-08.
28. As a manager, I want the 404 page to show lights that drift and never settle, so that a lost page still has a small joke.
29. As a manager, I want one light to show its label at rest, such as "The Blue Tent · 100.31", so that I learn without a word that a light has a label.
30. As a manager, I want a tap anywhere in the scene to select the nearest light, so that my finger never misses.
31. As a manager, I want to slide my finger sideways across the scene to move from light to light, so that I can read every light in one motion.
32. As a manager, I want a vertical swipe on the scene to still scroll the page, so that the scene never traps my scroll.
33. As a manager, I want a short hint "TAP OR SLIDE" the first time I see a scene, so that I know the scene does something.
34. As a manager, I want the hint to go away after my first touch and stay away, so that it does not nag me.
35. As a manager, I want a label near an edge of the scene to flip inward, so that it is never cut off.
36. As a manager, I want the scene to play again when I scroll back to the hero, so that I can watch it again without a reload.
37. As a manager who turns on reduced motion, I want the settled chart at once, with no drift, so that the page does not move.
38. As a manager with a slow phone, I want the scene to stop its work when it is at rest, so that it does not drain my battery.
39. As a manager on the light theme, I want the hero and its scene to stay dark, so that the scene reads the same in both themes.
40. As a manager of the NorCal league, I want the scene in my brand colors, with the orange accent for the flare, so that the scene looks like my league.
41. As a manager, I want only the first hero of a page to move, so that a page with many heroes stays calm.
42. As a manager, I want a link, a button, or the grade popover inside a hero to still work, so that the scene never blocks a tap on the content.
43. As a manager, I want the text of a hero to stay as readable as before, so that the scene never lowers the contrast.
44. As the commissioner, I want a new page hero to fit the six places with no new layout, so that a new page looks right by default.
45. As the commissioner, I want a hero with no scene to keep the static grid, so that only the pages that earn motion get it.
46. As a developer, I want `Hero` to accept the six places and no free content, so that the inconsistency cannot come back.
47. As a developer, I want the heading level of a hero set by a prop, so that a hero inside a page can be an `h2` with the same look.
48. As a developer, I want the scene to take plain data as a prop, so that the scene follows ADR 0012 and is easy to test.
49. As a developer, I want the math of the scene, such as the place of each light and the nearest light to a tap, in pure functions, so that a unit test can check it with no canvas.
50. As a developer, I want the readability floor check to still pass on every page with a scene, so that the scene cannot break ADR 0025.

## Implementation Decisions

### The hero slots

- `Hero` takes six named props in a fixed order: `eyebrow`, `title`, `meta`, `feature`, `stats`, `action`. Only `title` is required. `Hero` takes no `children` (decision 01 of the map, the grill of 2026-11-07).
- `Hero` keeps its `label` prop for the name of the region. It gets a heading-level prop with the values 1 and 2. The level changes the element, not the look.
- An absent slot renders no element and no gap.
- The styles of the slots are fixed inside `Hero`. A page cannot pass a class to a slot.
  - `eyebrow`: the mono font, the meta size, uppercase, the wide tracking, the accent text color.
  - `title`: the headline size of 40px, Space Grotesk 300, the tight tracking, balanced wrap. One style on every hero.
  - `meta`: 16px, the body leading, the second text color on dark. It holds one or two lines.
  - `feature`: free content, laid out by the page.
  - `stats`: a row of `Tile`s with the `sp-2` gap.
  - `action`: the links, the buttons, and the share bar.
- The gaps are `sp-6` between slots and `sp-2` from the eyebrow to the title.
- One faded hairline in the `rule-dark` color sits above `stats`, from the `tablet` tier up only. It is transparent at both ends.
- The text of each slot stays on the plate of the band color, as now, so the contrast of the text is the contrast of its role pair.

### The layout

- On a phone the slots stack in one column in the slot order.
- From the `tablet` tier up, the hero takes two rows. The top row holds the eyebrow and the title on the left and `meta` on the right, set apart to the two edges. `feature` sits between the rows. The bottom row holds `stats` on the left and `action` on the right, set apart to the two edges. A hero with a scene places the scene in the open middle.
- Two columns with `feature` on the right lost in decision 01, because the team rows broke after each word at 640px.

### The move of each hero

The spec moves the content that exists. It adds no number and no copy, except the two titles named here.

| Hero | eyebrow | title | meta | feature | stats | action |
| --- | --- | --- | --- | --- | --- | --- |
| Matchup of the Week, home | the week and the pick | the winner "by" the margin | the reason | the team rows | none | the link to the week |
| Matchup of the Week, week page | the week and the pick | the winner "by" the margin | the dates | the team rows and the photo frame | none | the share bar |
| Manager | the record line | the team name | the owner | the avatar, the grade mark with its popover, the week chips | the odds tiles | none |
| Power rankings | the week | the name of the rank-1 team | the record line | none | the odds tiles | the link to the manager page of the rank-1 team |
| Midseason takeover | the season and the week | the title of the opener | none | none | the leader tiles | the link to the report |
| Midseason opener | the season and the week | the title of the opener | the lead line | none | the leader tiles | the link to the finale |
| Act title | the act number | the act title | none | none | none | none |
| Analyzer form | the name of the tool | the title of the form | the line under it | the loading state | none | none |
| Analyzer result | the side | the verdict word | the reason | the fairness block | none | none |
| 404 | none | "Page not found" | the line under it | the big "404" | none | the two buttons |

The ticket of each hero checks this row against the code and records a change in its close comment.

- **The blurb of the Matchup of the Week moves out of the hero**, into a paragraph directly under it in the same chapter. No "Read more" control (decision 05, the default of the ticket: no new control and no new toggle test).

### The hero scene

- A `scene` prop on `Hero` takes the data of one scene. A hero with no `scene` keeps the static CSS grid. The page sets `scene` on its first hero only (decisions 06 and 07).
- The scene is a client component on one Canvas 2D context. `Hero` stays a server component. The device pixel ratio is capped at 2. A `ResizeObserver` sets the size (ADR 0027).
- No three.js, no WebGL, and no new dependency (ADR 0027).
- The data of a scene is plain, so the scene reads no file and no config (ADR 0012). Its shape:
  - a list of lights, each with an x value, a y value, a label, and a tone of `flare`, `bright`, or `dim`
  - zero or more guide lines, such as the league median or the median of each week, each with a label
  - an optional margin mark between two lights, such as "+1.43"
  - the index of the light that shows its label at rest
  - a mode: `settle`, or `drift` for a scene that never settles
- The math of the scene lives in pure functions: the place of each light in a box, the nearest light to a point, the side of a label near an edge, and the place of the margin mark so that no label covers it.
- **Phone:** the scene is a band of about 130px under the eyebrow, the title, and the meta, so the reader gets the words first. **From the `tablet` tier up:** the scene fills the open middle. No light sits under text (Brian, 2026-11-08).
- **The settle:** the lights start scattered, drift in, and settle in about 1.5 s with a strong ease-out (Brian, 2026-11-08). Thin lines then draw between the lights in x order. This is variant A, "Constellation", of decision 06.
- **Dust:** a faint dust of 40 to 80 tiny points drifts behind the lights. It stops at rest too.
- **Entry and re-entry:** an `IntersectionObserver` at about 40 percent starts the settle. The settle plays again after the hero fully left the view and comes back.
- **At rest the loop stops.** A tap or a slide draws one frame.
- **Tap:** a tap anywhere in the scene selects the nearest light. No tap misses, and a tap does not replay the scene.
- **Slide:** a horizontal drag moves the selection to the light nearest the finger. The canvas uses `touch-action: pan-y`, so a vertical drag scrolls the page. The scene never calls `preventDefault`.
- **Label at rest:** one light shows its label after the settle. A label near an edge flips to the inner side of its light and stays inside the scene.
- **The margin mark** sits where no label covers it, also while the winner is selected. Decision 06 found the label of the winner over "+1.43", and this spec must fix it.
- **Hint:** the caption "TAP OR SLIDE", in the mono meta style and a muted color on dark, sits in a corner of the scene with no light. It fades after the first touch on any scene. A flag in `localStorage` keeps it gone for that reader. Each read and write of the flag sits in a try and catch, and the scene works with no storage.
- **During the settle** a tap or a slide does nothing. The selection waits for rest. This is known and accepted.
- **Reduced motion:** the settled chart draws at once. No drift, no dust motion, and no re-entry replay.
- **Content stays on top:** the canvas sits under the content and takes no tap meant for a link, a button, or the grade popover.

### The scene of each hero

From decision 07.

| Hero | Mode | Lights | Guide | Flare | Label at rest |
| --- | --- | --- | --- | --- | --- |
| Matchup of the Week, home and week page | settle | 12 teams, sorted low to high by the points of the week | the league median | the two teams of the Matchup, with the margin mark | the winner of the Matchup |
| Manager | settle | one per played week: x the week, y the points | the median of each week | none: a win is `bright`, a loss is `dim` | the latest week |
| 404 | drift | a scatter | none | none | none |
| Power rankings, midseason opener and takeover, analyzer form and result, act titles | no scene | | | | |

- **Revision, Brian, 2026-11-08:** the scene stays only where it shows something the page does not show. The power rankings, the midseason, and the analyzer scenes leave the spec, and those heroes keep the static grid. Stories 24 to 27 leave with them. The rankings hero gets a link to the manager page of the rank-1 team, because the ladder starts at rank 2.
- The data of each scene comes from the published files that the page already loads. The Matchup uses the week file: its teams, its matchups, its median, and its pick. The manager uses the managers file.

### The colors of the scene

From decision 03.

- The canvas draws three colors only: `accent`, `on-dark`, and `on-dark-muted`. Each is a plain hex in every client and in both themes.
- The grid and the glow stay in the CSS layer of the hero texture. Two grid roles change with the theme, and CSS follows a switch of the theme with no redraw.
- At mount the scene reads each color from a hidden probe element with the computed `color`, and passes the `rgb()` string to `fillStyle` as it is. A dim light uses `globalAlpha`. The scene never passes a raw `var()` to `fillStyle`.
- The flare uses `accent` on every client. On NorCal that is the orange, not the gold `accent_text` (Brian, 2026-11-07).
- Fallback if the scene must read nothing from the DOM: the build writes the three triplets from the dark set into the client values, and the page passes them as a prop.

### The records

- ADR 0027 is written: the hero scene settles on a canvas. It supersedes the scan line and the rule of transform and opacity only of ADR 0024, for the hero canvas alone.
- The scan line goes. Its CSS rule and its keyframes leave the global stylesheet.
- `GLOSSARY.md` holds the terms Hero slot and Hero scene.

### The order of the tickets

1. The slots first: `Hero` takes the six slots, and the heroes move to them. These tickets ship the consistency fix alone.
2. Then the scene: the pure math, the canvas component, and the scenes of the Matchup and the manager.
3. Then the other scenes: power rankings, midseason, and the 404.
4. Last, the analyzer form with its change from `drift` to `settle`.

The scene can leave the spec at any step, and the slots still ship.

## Testing Decisions

A good test checks what a manager sees and does: the regions, the headings, the text, the order of the parts, and the response of the scene to a tap or a slide. It does not check a class name, a private function of a component, or the order of calls. A test uses the existing fixtures of real data. No test uses a mock mode.

The seams, from the highest down. Brian checks these seams with the spec.

1. **The built page in Chromium.** Playwright on the static export of each client, the seam of the readability floor (ADR 0025). It checks what jsdom cannot: the layout of the slots at 390px and at the `tablet` width, the hairline from the `tablet` tier up only, no sideways scroll, the canvas on the first hero only, the settled chart under reduced motion, a tap that selects the nearest light, a vertical swipe that scrolls, the hint once, and the floor on each page with a scene. Prior art: `apps/site/e2e/floor.spec.ts` and the project `rules` of the Playwright config.
2. **The pages and the heroes in Vitest.** Each hero rendered from a fixture: the region, the heading at its level, the text of each slot in the slot order, no empty slot in the markup, and no scene where none belongs. Prior art: `packages/design/site/parts/look.test.tsx` for `Hero`, the tests of each hero, such as `manager-hero`, `matchup-of-the-week`, `power-rankings`, and `analyze-result`, and `apps/site/src/reduced-motion.test.tsx` for content at rest at once.
3. **The math of the scene.** The pure functions, with no canvas: the place of each light in a box, the nearest light to a point, the side of a label near an edge, the place of the margin mark clear of every label, and the data of each scene built from a real fixture. This is the one new seam. Prior art for a pure test next to a part: `packages/design/site/parts/photo-frame` and its `initialsOf`.

Two guards:

- The brand test holds `accent`, `on-dark`, and `on-dark-muted` equal in the light set and the dark set of each client. Prior art: `apps/site/src/app/brand-tokens.test.ts`.
- The readability floor passes on every page of `FULL_FLOOR_PAGES` before and after the change.

The analyzer result and the analyzer form after a verdict need the live API. The floor check keeps them out (ADR 0025). Their evidence is a screenshot from a run against the real API, and the Vitest seam renders the result from the existing recorded response.

## Out of Scope

- A canvas on any surface other than the first hero of a page. ADR 0027 allows the hero scene only.
- A new number, new copy, or a new published field. The scene draws data that is already published, and the slots move the content that exists. The two titles in words are the only new text: the Matchup title and "Page not found".
- A change to the pipeline.
- Motion from the tilt of the phone. iOS asks for a permission first.
- A font weight under 300.
- Three.js or WebGL.
- A "Read more" control for the blurb of the Matchup.
- A tap or a slide during the settle.
- The variants B, "Comet", and C, "Pulse", of decision 06.
- A scene on the power rankings, the midseason, or the analyzer heroes (Brian, 2026-11-08).

## Further Notes

- The layout and the type come from the Tide template of Scrolltide, and the idea of the scene comes from the Astera template. We wrote our own code. The raw prompts of Scrolltide are paid source, and the repo is public, so no source of a template is in the repo.
- Weak spots from the prototype of decision 06, for the ticket of the scene: the lights look random until about the last 0.5 s of the settle, and the two red lights of a close Matchup sit close, so a slide jumps fast between them.
- The easter-eggs PR #19 places an egg on the 404 page. The ticket of the 404 hero keeps that egg working, whichever PR merges first.
- Space Grotesk 300 is already loaded, so the title needs no font change.
- No primary source confirms how Safari on iOS reads `oklch` or `color-mix` strings in `fillStyle`. The scene uses `rgb()` strings only, so it does not depend on it.
