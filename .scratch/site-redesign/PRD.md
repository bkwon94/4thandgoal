# Site redesign: every route in the shared look, dark by default

Status: ready-for-agent
Date: 2026-11-05
Apps: site. The site gets the shared look on every route of both clients, dark by default, with a light option. The pipeline does not change.
Spec branch: `site-redesign`.
Source: the map `.scratch/site-redesign/MAP.md` and decision tickets 01 to 13. ADR 0024, which supersedes ADR 0006 and part of ADR 0007. The prototypes are the boards on the Design canvas https://claude.ai/artifact/4cFaYVh4Sm9Cw68G7FEds8.
Tickets: none yet. `cpc:to-tickets` writes them.

## Problem Statement

The site keeps the look of the printed report: Helvetica, a black masthead, white pages, and grey cards (ADR 0006). It reads as print. Brian wants the first reaction of a manager to be "wow, this looks incredible" and "this is so easy to use and to read".

The pages have five more problems for a manager.

1. Each client picks a menu layout, `hamburger`, `bar`, or `tabs`, so the navigation differs per client, and on a phone it hides behind a button.
2. The trade analyzer form is hard to use. Its dropdowns cover the screen and are hard to close. The third team is hard to find. The send-to control is not clear.
3. The rankings and the managers pages use dense tables, with small cells and 12px text at phone width.
4. Light is the default, and NorCal has only a dark set, so NorCal readers get no light option and CPC readers start on a white page.
5. No check proves that a page is easy to read. Contrast is checked only on the tokens, not on the page.

## Solution

One shared look paints every route of the site in both clients: home, week, analyzer, managers, rankings, and 404. The look is the blend of Instrument and Glass HUD (ADR 0024): Space Grotesk and JetBrains Mono, a loud dark hero with the grid, the corner brackets, the brand glow, and a scan line, plain cards and tiles, round photo frames, and a staggered rise.

Each brand keeps its colors, its logo, and its copy. Dark is the default for every client. Each client has a light set and the theme button. In light, the page and the cards go light, and the hero stays dark.

On a phone, a dock at the bottom holds the destinations, and a week chip in the top band opens the weeks of the season. On a desktop, a pill bar holds the destinations, and the week page adds the chapter rail.

Each page gets the layout that Brian chose on the canvas. The week page is one scroll of chapters, with no tabs. The analyzer is one scroll, the Stack, with a picker that removes the send-to control. Rankings is a Ladder of cards. Managers is a set of cards with the grade as the hero number.

A readability floor runs as a check on the static export of each client: text size, contrast, tap targets, and no sideways scroll. Brian gives the verdict on screenshots of each route, at phone and desktop width, in both clients and both themes.

## User Stories

### The first view

1. As a manager, I want the site to open in dark, so that the first view looks like a broadcast and not like a printed page.
2. As a manager, I want each page to open with one big hero, so that I see the main fact of the page first.
3. As a manager, I want the hero to carry the grid, the brackets, the glow, and a scan line on entry, so that the page feels made for the league.
4. As a manager, I want the content under the hero to rise in a short stagger, so that the page feels alive without a wait.
5. As a manager who turns on reduced motion, I want no rise, no scan line, no bar growth, and no tap scale, so that the page does not move.
6. As a CPC manager, I want the site in CPC red and black with the CPC logo and copy, so that it is still our league site.
7. As a NorCal manager, I want the site in NorCal gold and orange with the NorCal logo and copy, so that it is still our league site.

### The theme

8. As a manager, I want the theme button in the top band on every page, so that I can switch to light.
9. As a manager, I want my theme choice to hold across visits, so that I choose it once.
10. As a manager who chose light, I want the page to open in light with no dark flash, so that the switch does not blink at me.
11. As a manager with no stored choice, I want the page to open in dark with no light flash, so that the first paint is the right one.
12. As a manager with scripts off, I want the page in dark, so that I still see the default look.
13. As a NorCal manager, I want a light option, so that I can read the site in a bright room.
14. As a manager in light, I want the hero to stay dark, so that the hero keeps its grid and glow.
15. As a manager in light, I want accent text that I can read on the light page, so that a red or orange word is not faint.

### The navigation

16. As a phone reader, I want a dock at the bottom with Home, Week N, Rankings, Managers, and Trade, so that every destination is one tap away.
17. As a phone reader, I want the dock to stay on screen at every scroll, so that I never scroll back up to move.
18. As a phone reader, I want an icon and a label for each dock item, so that I know where each tap goes.
19. As a reader, I want the current destination marked in the dock or the pill bar, so that I know where I am.
20. As a reader, I want a "WK 08" chip in the top band, so that I can see and change the week from any page.
21. As a reader, I want a tap on the week chip to open a strip of the weeks of the season, with the current week marked, so that I can jump to any week.
22. As a desktop reader, I want a pill bar with full labels in the top band, so that the destinations are in plain view.
23. As a desktop reader on the week page, I want the chapter rail on the left that marks the chapter in view, so that I can jump to a chapter.
24. As a client owner, I want each client to list its destinations and their labels, and nothing more, so that the look owns the navigation.

### The home page

25. As a manager, I want the home page to open on the Matchup of the Week of the latest week, so that I see the story of the week first.
26. As a manager, I want the margin as the big number of the home hero, with both teams, avatars, scores, the reason, and the first sentence of the blurb, so that I get the matchup in one look.
27. As a manager, I want a "Read Week N" button in the home hero, so that I can go to the full week.
28. As a manager, I want the four numbers of the latest week on the home page, so that I see the week at a glance.
29. As a manager, I want the top three of the Power Rankings on the home page, with a link to all teams, so that I see who leads.
30. As a manager, I want a tile for each tool of the client, with an icon and one line, so that I find the analyzer and the managers.
31. As a manager, I want a row for each published week, newest first, with its dates and its Matchup of the Week, so that I can reach any past week.
32. As a client owner, I want the home parts to come from the packages of the client, so that a client with no rankings shows no rankings part.

### The week page

33. As a manager, I want the week page to open on the Matchup of the Week, with its reason, the margin, both teams, their top players, the share bar, and the full blurb.
34. As a manager, I want four numbers under the hero: the top score, the median, the closest margin, and the Game Changer gap, so that I get the week at a glance.
35. As a manager, I want a card for each game, by top score, with both avatars, both scores, and a share bar, so that I see every result.
36. As a manager, I want a tap on a game card to open its recap, with a brand edge on the open card, so that I read the recap only when I want it.
37. As a manager, I want one "Manager page" link in an open recap, so that I can reach a team from a game.
38. As a manager, I want the Game Changer in a round photo frame with three tiles for scored, projected, and over, so that the big game of a player stands out.
39. As a manager, I want each award as a tile with its name, a photo, the points, the player, and the team, so that the awards read in a grid.
40. As a manager, I want a chip for each position, QB, RB, WR, TE, and DEF, with the top three of the chosen position, so that I compare the leaders.
41. As a manager, I want a card for each trade, with each side and the players it gets, so that I see the trades of the week.
42. As a manager, I want a bar for each team against the median line, with its avatar, so that I see who beat the median.
43. As a manager, I want the standings with every team, its avatar, a playoff tick, and a brand line under the last playoff spot, so that I see the race.
44. As a manager, I want a card for each game of next week, with a Must Watch reason and a key player on bye, so that I know what to watch.
45. As a manager, I want links to the past week and the next week at the end of the page, so that I can move through the season.
46. As a manager, I want every chapter on one scroll, with no tabs, so that I miss nothing.

### The analyzer

47. As a manager, I want the analyzer as one scroll with the title "Trade Analyzer" and "Who gets what?", so that I know what the page does.
48. As a manager, I want a teams row with an avatar for each team of the trade and a "+" slot that says "<n> of 4", so that I can add a team.
49. As a manager, I want a tap on "+" to open a short sheet of every team, with the teams already in the trade dimmed, so that I add a team in one tap.
50. As a manager, I want one card for each team that says what it gets, so that I build the trade as "who gets what".
51. As a manager, I want each picked player to show "from <team>", so that I know where it comes from without a send-to control.
52. As a manager, I want a remove button on Team Three and Team Four, so that I can go back to two teams.
53. As a manager, I want "Add a player <team> gets" to open a short sheet with a tab for each other team, a search field, and the position chips, so that I find a player fast.
54. As a manager, I want a tap on a player row to toggle a check, so that I pick many players in one visit to the sheet.
55. As a manager, I want to close the sheet with Done, with the close button, or with a tap on the dim page, so that the sheet never traps me.
56. As a manager, I want the same picker for 2, 3, and 4 teams, so that a bigger trade is no harder.
57. As a manager, I want the "Grade the Trade" bar on the dock, so that it stays in reach at every scroll.
58. As a manager, I want the bar off until each team gives and gets at least one player, with a line that says so, so that I know what is missing.
59. As a manager, I want the loading state to fold the form to a line of faces and show the hero with "Grading the Trade", so that I know the grade is on its way.
60. As a manager, I want the verdict to fill the hero, with the fairness block under it, so that the grade is the first thing I read.
61. As a manager in a trade of 3 teams or more, I want each team as one row with "Gives" and "Gets", and each player tagged "TO" or "FROM" a team, so that I follow each player.
62. As a manager, I want an error box with the message and "Try Again" above the bar, with the form unlocked, so that I can fix the trade and try again.
63. As a manager of a client with the finder, I want the "Find a Trade" card under the form, so that I can ask for a trade.
64. As a manager, I want up to three finder cards, each with the swap, the Fairness pill, the reasons, and "See the Full Result", so that I can choose one.

### Rankings

65. As a manager, I want the team at rank 1 in the hero with a big "01", its record, its movement, and three tiles for Playoff, Bye, and Seed.
66. As a manager, I want a card for each other team with its rank, avatar, name, record, movement, and playoff odds with a short bar, so that I read the ranking at phone width.
67. As a manager, I want a tap on a ranking card to open the ranks of Stand, Form, Sched, and Pts, the blurb, and a link to the manager page, so that I see why a team sits there.
68. As a manager, I want week chips on the ranking, so that I can see the ranking of another week.
69. As a manager, I want a note that says how the four parts make the rank, so that the rank is not a black box.

### Managers

70. As a manager, I want one card for each team in standings order, with the avatar, the name, the record, the power rank, the playoff odds, and the grade letter in a box.
71. As a manager, I want the grade text under the grade box, such as "Deep at TE. Thin at WR.", so that I know what the grade means.
72. As a manager, I want the whole manager card to be a link, so that I do not aim for a small link.
73. As a manager, I want the grade letter as the big number of the manager hero, with the grade text beside it, so that the grade reads first.
74. As a manager, I want a W or L chip for each week in the manager hero, so that I see the season in one row.
75. As a manager, I want Season So Far as a line of the points of each week against the dashed median line, with a filled dot for a win.
76. As a manager, I want Roster as a tile for each position slot with its rank and its depth, then the four grade parts with their weights and ranks.
77. As a manager, I want Best Adds and Top Performers in round photo frames with the points on the right.
78. As a manager, I want Moves as three tiles for adds, drops, and trades, then one row for each week.
79. As a manager, I want a back link to all managers, so that I can move to the next team.

### The 404 page

80. As a reader on a dead link, I want a hero with a big "404" and a plain line about why, so that I know the page does not exist.
81. As a reader on a dead link, I want a "Go to Week N" button and a "Go Home" button, so that I get back in one tap.

### Photos

82. As a manager, I want each team to show its Sleeper avatar, so that I spot my team fast.
83. As a manager, I want each player headshot in a round frame on the brand glow, cropped at the shoulders, so that photos look the same everywhere.
84. As a manager, I want the initials in the frame when no image exists, so that a missing headshot does not leave a hole.

### Readability

85. As a manager, I want prose at 16px or more and other text at 11px or more, so that I read the site without a zoom.
86. As a manager, I want every link and button at 44px or more, so that I hit it with a thumb.
87. As a manager, I want no sideways scroll at 390px, so that a page never slides under my thumb.
88. As a manager, I want every text to pass the AA contrast, so that I read it in sun and in the dark.
89. As Brian, I want a check that fails a PR when a page breaks the readability floor, so that a later change cannot undo it.
90. As Brian, I want screenshots of each route at phone and desktop width, in both clients and both themes, so that I give my verdict from one place.
91. As Brian, I want the local dev server started after each route of the build, so that I can look at it early.

### The fonts and the speed

92. As a manager, I want the fonts to load from the site itself, so that no outside host slows the page.
93. As a manager, I want the number columns to stay aligned before the mono font loads, so that the page does not jump.
94. As Brian, I want a check on the byte budget of the fonts, so that the fonts never grow past 56,000 bytes.

## Implementation Decisions

### Decision 12: how dark becomes the default

- The site keeps the `.dark` override block of ADR 0007. The brand CSS still paints the light set first, in `@theme static`, and the dark set under `.dark`. So every `dark:` variant of the components stays.
- The build puts the `dark` class on `<html>` for every client. The static export ships dark, so a reader with no stored choice or with scripts off gets dark at the first paint.
- The boot script removes the `dark` class when the stored choice is `"light"`. It does nothing for a stored `"dark"` or for no choice. It stays inline and first in the head, so a light reader sees no dark flash.
- `paintOf` loses the branches of a one-set brand. With both sets required, every client gets the root class `dark`, the boot script, and the theme button. The function may shrink to constants. The comment on the root layout changes to match.
- `storeTheme` and the storage key `cpc.theme` stay. The theme button stores `"light"` or `"dark"`, as now.
- The check of the readability floor sets the theme with `addInitScript` on `cpc.theme`, then asserts the class on `<html>`. So the boot script is the one path to light in the check, as for a reader.
- We chose this over a `.light` override because the inversion changes every `dark:` variant in the components, for no gain to the reader. The record goes into ADR 0024, which now says the `.dark` override stays until this decision.

### The look

- The fonts: Space Grotesk for text and headings, JetBrains Mono for numbers, scores, and small uppercase labels. Both self-host with `next/font/local`, one Latin variable woff2 file each, `display: "swap"`, `preload: true`. JetBrains Mono sets `adjustFontFallback: false`, with a Menlo or Courier New fallback face. Each font ships with its `OFL.txt`.
- The radii: 24px for the hero, 20px for a card, 18px for a tile, and a full pill for a button and a bar.
- The fonts and the radii of the look live in the `@theme static` block of the global CSS of the site, beside the spacing and type tokens. The class names `rounded-card`, `rounded-sm`, and `font-heading` stay.
- The space: the hero has 28px of inner space on top and bottom and 24px on the sides. A card has 16px. The page gutter is 16px.
- The hero is the one loud surface of a page: the 24px grid texture, the corner brackets, the brand glow, and a scan line on entry. It sits on the `band` color in both themes.
- The motion: content rises in a stagger, 0.7s on `cubic-bezier(.16,1,.3,1)`. Bars grow once. A recap opens in 0.3s. A tap scales to 0.98. Motion uses transform and opacity only. Reduced motion turns all of it off.
- The photos: a team row shows its Sleeper avatar. A headshot sits in a round frame on the brand glow, cropped at the shoulders. With no image, the frame shows the initials.

### The brand schema

- `brand.toml` holds only the `light` and the `dark` sets. Both are required. The schema keeps `additionalProperties: false`, so a stale `[fonts]` key or a radius key fails the build.
- Both clients drop `radius_card`, `radius_small`, and `[fonts]`.
- NorCal gains a light set, and CPC gets a light set of decision 09. The rows map to the keys of `brand.toml` as below. Two roles are new, `raised` and `grid`, because no key holds them now.

| Role of decision 09 | Key | CPC | NorCal |
| --- | --- | --- | --- |
| page | `page` | `#f4f4f4` | `#f5f3ef` |
| card | `card` | `#ffffff` | `#ffffff` |
| raised | `raised`, new | `#ebebeb` | `#ecebe8` |
| rule | `rule` | `#e0e0e0` | `#e2e0dc` |
| text | `text` | `#141414` | `#1c1917` |
| ink 2 | `ink_2` | `#3a3a3a` | `#3f3a35` |
| muted | `muted` | `#666666` | `#6b6359` |
| accent ink | `accent_ink` | `#a52e25` | `#9a3412` |
| accent | `accent` | `#b8342a` | `#c2410c` |
| bar off | `bar_off` | `#dddddd` | `#e2ddd3` |
| band, the hero surface | `band` | `#141414` | `#0a0a0a` |
| hero grid lines | `grid`, new | `#1c1c1c` | `#181818` |
| hero glow | `accent_glow` | `#b8342a` at 45% | `#e0a526` at 35% |
| hero text | `on_dark` | `#ffffff` | `#f5f0e6` |
| hero ink 2 | `on_dark_2` | `#cccccc` | `#d6d0c4` |
| hero muted | `on_dark_muted` | `#999999` | `#a8a29a` |
| hero accent text | `accent_text` | `#f2a59e` | `#e0a526` |
| hero rule | `rule_dark` | `#333333` | `#2e2e2e` |
| hero raised | `chip_dark` | `#262626` | `#232323` |

- The dark set of each brand keeps its values. It gains `raised` and `grid` with the values of the dark boards on the canvas. The hero roles of the dark set equal the hero roles of the light set, so the hero is the same in both themes.
- NorCal gold is never text on a light surface. In light it shows only as the hero glow and as the hero accent text.
- Roles that the look no longer paints, such as `card_band` and `pick`, stay only if a component still reads them. The build ticket removes each unread role and its test.

### The navigation and the shell

- The `layout` key of `[menu]` in `client.toml` goes away. A client keeps only its list of items and their labels. The `hamburger`, `bar`, and `tabs` layouts of the masthead go away.
- The shell is the top band, the dock, the pill bar, the week chip, the strip of weeks, and the theme button.
- On a phone, the top band holds the brand mark, the week chip, and the theme button. The dock floats at the bottom with an icon and a label for each item, 11px or more. It stays on screen at every scroll.
- On a desktop, the top band holds the brand mark, the pill bar with full labels, the week chip, and the theme button. It stays on screen at every scroll, as the dock does on a phone. The week page adds the chapter rail on the left.
- The week chip reads "WK NN". A tap opens a strip of the weeks of the season, with the brand edge on the current week.

### The pages

- **Home** is the Front page of decision 08: the intro, the hero on the Matchup of the Week of the latest week, its four numbers, the top three of Power Rankings, a tile for each tool, and a row for each published week. Each package still gives its own part through the registry.
- **Week** has the order of decision 05: the hero, the four numbers, every game with tap recaps, Game Changer, Awards, Position leaders, Trades, the median game, Standings, Next week, and the footer. No tabs. The chapter port of the week package stays, so a package still gives a chapter.
- **Analyzer** is the Stack of decision 06, with the picker "Gets", in the states empty, loading, result, error, and 3 teams or more. The finder card follows the Stack for a client with `finder = true`.
- The body of `POST /analyze` stays the same. Each pick becomes a `gives` entry of its source side, with `to` set to the team of the card. The result content stays as the grade-clarity decision 04 sets it. The error lines stay as `toErrorLine` writes them. The placeholder "Suggested Counters · No counters yet." stays.
- **Rankings** is the Ladder of decision 07: the hero for rank 1, the week chips, a card for each other team that opens its four part ranks, and the note on the parts.
- **Managers** is the Cards of decision 07. The index is a card per team in standings order. The manager page has the back link, the hero with the grade as the big number and a W or L chip per week, then Season So Far, Roster, Best Adds, Top Performers, and Moves.
- **404** is the hero of decision 08 with "ERROR // PAGE NOT FOUND", a big "404", the line "This page does not exist. The link may be old, or the week is not out yet.", and the two buttons "Go to Week N" and "Go Home".
- One pattern holds for each kind. A ranked list is a column of cards on a phone, with the rank in mono on the left and one number on the right. A table stays only where it has five columns or fewer. A manager card shows the avatar, the name, the record, one key number, and the grade box.
- A team in a row: the whole row is the link. A game card that opens its recap is one button, so its team names are plain text.
- Every page uses only the data that the pipeline publishes now and that the API returns now.

### The glossary

The redesign breaks some terms of the site section of `GLOSSARY.md`. The build rewrites them as below.

- **Masthead** becomes **Top band**: the band at the top of every page with the brand mark, the week chip, and the theme button, and on a desktop the pill bar.
- **Menu** stays the list of the destinations of a client. It shows as the dock on a phone and as the pill bar on a desktop.
- **Menu button** and **Compact bar** go away. The dock and the top band take their jobs.
- **Sheet** changes meaning: the short panel that rises from the bottom over the dimmed page, such as the team list and the player picker of the analyzer.
- **Black chapter** goes away. **Chapter** becomes one part of a page under its heading, such as Awards of the week page. "Card" names a plain surface, and "Tile" names a small card with one number.
- **Page** becomes the surface behind the cards: dark in the dark theme and light in the light theme.
- **Hero** widens from the top of a manager page to the loud top surface of each page, which stays dark in both themes.
- **Shell** becomes the top band, the dock, the pill bar, the week chip, and the theme button.
- **Pill bar** is new: the row of destinations with full labels in the top band of a desktop.

### The records

- ADR 0024 gets the choice of decision 12. ADR 0007 keeps its `.dark` override and its superseded line.
- ADR 0022 changes its lines on fonts in `brand.toml`.
- A new ADR fixes the readability floor as a rule, beside ADR 0016, when the check is built.

## Testing Decisions

A good test checks what a reader or a build sees: the built page, the static export, the CSS that the build writes, or the result of the schema. It does not check the inner state of a component.

### The seams

1. **The readability floor**, a new seam. It is the highest seam: Playwright on the static export of each client, in `build-each-client.mjs` after `check:export`. It runs in CI on each PR, and not in `check:fast`.
   - axe with the rule `color-contrast` checks contrast at the WCAG AA split. An `incomplete` result fails too.
   - A `page.evaluate` scan checks text size, tap targets, and the scroll width at 390px. Prose is a `<p>` or an element with `data-prose`, at 16px or more. Other text is 11px or more. A link inside prose is exempt from 44px, and the check prints each exempt link. The check prints the count of each tier.
   - The full floor runs in both themes at 390px and at desktop width, on 7 pages per client: home, the latest week, rankings, the managers index, the manager page with the longest team name, the empty analyzer, and 404. It also runs on three open states: an open recap on the week page, an open card on the Ladder, and the open strip of weeks.
   - A fast sweep loads every other built page once, in dark at 390px, and checks only text size and sideways scroll.
   - The analyzer states that need the live API stay out of the check: the team list, the picker sheet, loading, the result, and the error. Brian's verdict covers them, because a fake API is a mock.
   - `check.yml` gets a Chromium install step. The first build ticket measures the real time. The estimate is 1.5 to 2.5 minutes.
2. **The token tests**, existing. `brand-contrast.test.mjs` holds every text pair of each set at 4.5 to 1, the hero pairs among them. `brand-tokens.test.ts` reads the look in the global CSS. Its ban on `next/font` narrows to `next/font/google` and the outside font hosts. New checks hold the font byte budget of 56,000 in total, exactly two font files, two font preloads on each page, and an `OFL.txt` for each font.
3. **The build of a client**, existing. `client-build.test.mjs` checks the paint order and that a brand with one set fails and names the missing set. `brand.test.ts` checks that the schema rejects a one-set brand, a `[fonts]` key, a radius key, and a `layout` key of the menu.
4. **The theme**, existing. `theme.test.ts` runs the shipped boot script string: no choice keeps `dark`, a stored `"light"` removes it, a stored `"dark"` keeps it, and a storage that throws keeps it.
5. **The page tests**, existing. The Vitest page and component tests under the site and `packages/design` change to the new markup. They check what a reader sees: the order of the chapters, the hero content, the parts that a package gives, and the analyzer body for `POST /analyze` from a pick.

### The proof for Brian

- Screenshots of each route, at phone and desktop width, in both clients and both themes, are the evidence of the visual acceptance tests. The analyzer states with the live API are screenshots too.
- The four points of decision 02 need a real run: a build of both clients, the fallback on iOS and Android, the cache headers of the Worker, and a measure of the layout shift.

### Prior art

- `check-export.mjs` for a check on the static export.
- `brand-contrast.test.mjs` and `brand-tokens.test.ts` for checks on the tokens.
- `theme.test.ts` for a test of the shipped boot script.
- `masthead-props.test.ts` and `page.test.tsx` for page tests.

## Out of Scope

- The pipeline and any new data. Each idea that needs new data goes on the list of the map, for a later pipeline spec. The list is empty.
- The waiver page. No client takes the `waiver` package, so no client builds it and Brian cannot judge it.
- A test of the first reaction with other managers. Brian's verdict is the proof.
- Timed tasks, such as "find your score in 5 seconds".
- A font or a radius per brand. A brand gets the look as it is.
- A change to the content of the analyzer result, the error lines, or the counters placeholder.
- A theme that follows the system setting. The default is dark, and the theme button is the one way to light.

## Further Notes

- The redesign ships as one spec branch, one PR, and one cutover.
- During the build, Claude starts the local dev server after each route, so Brian can look at it.
- The approved boards change in two places in the build: blurbs and recaps go to 16px, and the dock labels go from 10px to 11px.
- The grade fixtures of the analyzer name teams that are in no league now, so their avatars show initials. The fallback covers it.
- The managers file has no player list per roster, so Roster shows the rank of each position slot.
- The Compact bar goes away, because the dock stays on screen on a phone and the top band stays on screen on a desktop. Brian approved the spec with this choice on 2026-11-05.
- Decision 01 lists 19 checks that break with the schema change. The build ticket uses that list: `decisions/01-research-brand-schema-drops-fonts.notes.md`.
