# Site redesign: evidence

Spec: `.scratch/site-redesign/PRD.md`. Acceptance tests: `.scratch/site-redesign/ACCEPTANCE.md`.
Built from: `12486d0e`, on 2026-11-05. The agent gives no Test verdict. Brian gives one for each test.

## Setup

Two agents recorded this evidence. This file holds the CPC half and the tests with no client. The NorCal files come from the second agent.

1. The CPC export: `NEXT_PUBLIC_API_URL=http://localhost:8080 CLIENT=cpc pnpm --dir apps/site build`.
2. The local API: `CORNERSTONE_ALLOWED_ORIGINS=http://localhost:4173 make -C apps/api api`, on port 8080.
3. The server: `python3 -m http.server 4173 --directory apps/site/out` first. From AT-32 on, a copy of it that answers a missing path with `404.html` and status 404, like the `404-page` handling of the Worker.
4. The instrument: `agent-browser` 0.25.4. The light theme sets `cpc.theme` to `"light"`. The dark theme removes the key, because dark is the default.
5. Before each full-page shot, the page scrolls to the end and back, so each chapter that rises on view shows. The dock is fixed, so a full-page shot shows it where the first screen ends.
6. A test of both clients keeps its CPC files under `cpc/`. A test with its own evidence list takes the widths and the themes of that list.

## AT-1: Dark is the first paint with no stored choice

App: site
Then: `<html>` has the class `dark` in the first paint, and the page shows the dark set with no light flash.
Files: `evidence/AT-1/cpc/375-dark.png`, `evidence/AT-1/cpc/first-load.webm`, `evidence/AT-1/cpc/served-html.txt`
Observation: The served HTML of the home page has `class="dark ..."` on `<html>`, and the boot script removes it only for a stored "light". The 375 px shot shows the dark set, and the 34 frames of the recording have a mean luma of 17.9 to 35.0 out of 255: blank black frames before the first paint, then the dark page, with no light frame.

## AT-2: Dark with scripts off

App: site
Then: The page shows the dark set, and every chapter shows at rest.
Files: `evidence/AT-2/cpc/375-dark.png`
Observation: With scripts off (`--blink-settings=scriptEnabled=false`, and `window.__next_f` is undefined), `<html>` keeps the `dark` class. The full 375 px shot shows the dark set and every chapter from the hero to the Previous Week 7 link at rest.

## AT-3: A stored light choice opens in light

App: site
Then: The page opens in light with no dark flash, and `<html>` has no `dark` class.
Files: `evidence/AT-3/cpc/375-light.png`, `evidence/AT-3/cpc/load.webm`, `evidence/AT-3/cpc/state.txt`
Observation: With `cpc.theme` set to "light", `<html>` has no `dark` class and the 375 px shot shows the light page and cards under the dark hero. In the recording, the first 4 frames are blank black frames before the first paint, and the next frame is already the light page (mean luma 137 or more); no dark page frame shows.

## AT-4: NorCal has a light theme and the theme button

App: site
Then: The page goes light, with the NorCal light set of the spec: page `#f5f3ef`, white cards, and accent text `#9a3412`.
Files: see the NorCal entry

## AT-5: The hero stays dark in light

App: site
Then: The hero sits on the `band` color with the grid, the brackets, and the glow. The page and the cards are light. NorCal gold shows only in the hero.
Files: `evidence/AT-5/cpc/375-light.png`, `evidence/AT-5/cpc/768-light.png`, `evidence/AT-5/cpc/1280-light.png`
Observation: At 375, 768, and 1280 px in light, the hero sits on the dark band with the grid, the corner brackets, and the red glow, and the page and the four tiles are light. This is the CPC half; NorCal gold is in the NorCal entry.

## AT-6: The brand of each client

App: site
Then: CPC shows its red, its logo, and its copy. NorCal shows its gold and orange, its logo, and its copy. Both use Space Grotesk and JetBrains Mono.
Files: `evidence/AT-6/cpc/375-light.png`, `evidence/AT-6/cpc/375-dark.png`, `evidence/AT-6/cpc/768-light.png`, `evidence/AT-6/cpc/768-dark.png`, `evidence/AT-6/cpc/1280-light.png`, `evidence/AT-6/cpc/1280-dark.png`, `evidence/AT-6/cpc/fonts.txt`
Observation: The home page shows the CPC red buttons and accents, the CPC logo, and the CPC copy "Cornerstone Fantasy Football League" in both themes. `fonts.txt` shows the heading in `spaceGrotesk`, the big number in `jetbrainsMono`, and both fonts loaded. These six files are copies of the AT-14 shots.

## AT-7: The hero and the motion

App: site
Then: The hero shows a scan line once. The content under it rises in a stagger, and the share bars grow once.
Files: `evidence/AT-7/cpc/animations.txt`, `evidence/AT-7/cpc/load-1280.webm`, `evidence/AT-7/cpc/load-375.webm`
Observation: `animations.txt` lists 5 running animations after the load, with the `hero-scan` animation first. The recording frames show the hero content and the tiles fade and rise in over about 0.3 s after the first paint; the scan line and the bar growth are too small to read in the frames at this size.

## AT-8: Reduced motion

App: site
Then: No scan line, no rise, no bar growth, and no tap scale. All content shows at rest.
Files: `evidence/AT-8/animations.txt`, `evidence/AT-8/load-and-tap-375.webm`, `evidence/AT-8/state.txt`
Observation: With reduced motion on, `animations.txt` lists 0 running animations in the 1.5 s after the load. The recording shows the page at rest from the first painted frame, then the open recap of The Blue Tent card after the tap. The animation list covers the load only, not the tap.

## AT-9: The dock on a phone

App: site
Then: The dock stays at the bottom with Home, Week 8, Rankings, Managers, and Trade, each with an icon and a label. Week 8 is marked.
Files: `evidence/AT-9/cpc/375-light-end.png`, `evidence/AT-9/cpc/375-light-top.png`, `evidence/AT-9/cpc/375-dark-end.png`, `evidence/AT-9/cpc/375-dark-top.png`, `evidence/AT-9/cpc/dock.txt`
Observation: At 375 px the dock stays at the bottom both at the top and at the end of the week 8 page, with Home, Week 8, Rankings, Managers, and Trade, each with an icon and a label. Week 8 has `aria-current="page"` and a raised tile with a red mark in both themes.

## AT-10: The pill bar on a desktop

App: site
Then: The top band shows the brand mark, the pill bar with full labels, the week chip, and the theme button. Rankings is marked, and the top band stays on screen.
Files: `evidence/AT-10/cpc/768-light-scrolled.png`, `evidence/AT-10/cpc/768-light-top.png`, `evidence/AT-10/cpc/768-dark-scrolled.png`, `evidence/AT-10/cpc/768-dark-top.png`, `evidence/AT-10/cpc/1280-light-scrolled.png`, `evidence/AT-10/cpc/1280-light-top.png`, `evidence/AT-10/cpc/1280-dark-scrolled.png`, `evidence/AT-10/cpc/1280-dark-top.png`, `evidence/AT-10/cpc/state.txt`
Observation: At 768 and 1280 px the top band shows the logo, the pill bar with full labels, the WK 08 chip, and the theme button, and Power Rankings is the marked pill. After a scroll of 898 px the band stays at the top (`position: sticky`, top 0). At 768 px the pill bar sits on a second row under the brand row.

## AT-11: The week chip and the strip of weeks

App: site
Then: A strip shows weeks 6, 7, and 8, with the brand edge on week 8. A tap on week 7 opens the week 7 page.
Files: `evidence/AT-11/375-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/768-light.png`, `evidence/AT-11/768-dark.png`, `evidence/AT-11/1280-light.png`, `evidence/AT-11/1280-dark.png`, `evidence/AT-11/strip.txt`
Observation: A tap on WK 08 opens a strip with WK 06, WK 07, and WK 08, and WK 08 has the red edge and `aria-current`. A tap on WK 07 opened `http://localhost:4173/2026/week-07/` with the title "Week 7 · Cornerstone Fantasy Football League". At 375 px the strip covers the top of the page title.

## AT-12: The chapter rail

App: site
Then: The chapter rail on the left marks Standings.
Files: `evidence/AT-12/cpc/1280-light.png`, `evidence/AT-12/cpc/1280-dark.png`, `evidence/AT-12/cpc/marked.txt`
Observation: At 1280 px with Standings at the top of the view, the chapter rail on the left marks STANDINGS in red in both themes, and `marked.txt` shows `aria-current="location"` on Standings.

## AT-13: The client menu has no layout key

App: site
Then: Neither file has a `layout` key in `[menu]`, and a `layout` key fails the build with a message that names it.
Files: `evidence/AT-13/build-with-layout.txt`, `evidence/AT-13/menu-tables.txt`
Observation: Neither `client.toml` has a `layout` key: CPC lists its `[menu]` items only, and NorCal has no `[menu]` table. With `layout = "hamburger"` added by hand to CPC, the build fails with `menu.layout: is not a known key` and exit 1.

## AT-14: The home page order

App: site
Then: The page shows, in order: the intro, the hero with "1.43" as the big number and a "Read Week 8" button, the four numbers, the top three of Power Rankings led by All You Need Is Love, the tool tiles, and a row for weeks 8, 7, and 6.
Files: `evidence/AT-14/375-light.png`, `evidence/AT-14/375-dark.png`, `evidence/AT-14/768-light.png`, `evidence/AT-14/768-dark.png`, `evidence/AT-14/1280-light.png`, `evidence/AT-14/1280-dark.png`, `evidence/AT-14/order.txt`
Observation: The full pages show, in order: the intro, the hero with "1.43" as the big number and a "Read Week 8" button, the four numbers, Power Rankings led by All You Need Is Love with 3 rows, the Tools tiles, and Weekly Reports rows for weeks 8, 7, and 6. The order is the same at all three widths in both themes.

## AT-15: The NorCal home page

App: site
Then: The hero shows "10.62" as the big number. Power Rankings is led by Mitseeker5000. One weekly report row shows, for week 8.
Files: see the NorCal entry

## AT-16: The week page order

App: site
Then: The page shows one scroll with no tabs, in order: the hero, the four numbers, every game, Game Changer with Joe Burrow at 42.48, Awards, Position leaders, Trades, the median game, Standings, Next week, and the footer.
Files: `evidence/AT-16/cpc/375-light.png`, `evidence/AT-16/cpc/375-dark.png`, `evidence/AT-16/cpc/768-light.png`, `evidence/AT-16/cpc/768-dark.png`, `evidence/AT-16/cpc/1280-light.png`, `evidence/AT-16/cpc/1280-dark.png`, `evidence/AT-16/cpc/headings.txt`
Observation: The full pages show one scroll with no tab (`[role=tab]` count 0), in order: the hero, the four numbers, every game, Game Changer with Joe Burrow at 42.48, Awards, Position leaders, Trades, The median game, Standings, Next week, and the Previous Week 7 link. At 375 px some tile labels break inside a word: "PROJECT/ED", "+20.4/4", "UNDERPERF/ORMER", "OVERACHIE/VER", and "BENCHWARM/ER"; at 1280 px the award labels also break ("UNDERPER/FORMER").

## AT-17: A recap opens on a tap

App: site
Then: The card opens its recap with a brand edge. The recap holds one "Manager page" link.
Files: `evidence/AT-17/cpc/375-light.png`, `evidence/AT-17/cpc/375-dark.png`, `evidence/AT-17/cpc/768-light.png`, `evidence/AT-17/cpc/768-dark.png`, `evidence/AT-17/cpc/1280-light.png`, `evidence/AT-17/cpc/1280-dark.png`, `evidence/AT-17/cpc/links.txt`
Observation: The tapped card of The Blue Tent and London Cooking opens its recap with a red edge in both themes at all three widths. The open card holds one link, "Manager page of The Blue Tent" to `/2026/managers/1/`.

## AT-18: Position leaders

App: site
Then: The chapter shows the top three WR of week 8.
Files: `evidence/AT-18/cpc/375-dark.png`, `evidence/AT-18/cpc/1280-dark.png`, `evidence/AT-18/cpc/rows.txt`
Observation: After a tap on WR, the chip shows as selected, and the chapter lists Tee Higgins 32.5, Ja'Marr Chase 25.6, and Michael Wilson 22.8. The prose under the list still describes the quarterbacks, and at 1280 px the rail marks AWARDS, not POSITION LEADERS.

## AT-19: The analyzer, empty

App: site
Then: The page shows "Trade Analyzer", "Who gets what?", the teams row with Your Team, Team Two, and a "+" slot with "2 of 4", two empty cards, the line on what each team needs, and the "Grade the Trade" bar turned off on the dock.
Files: `evidence/AT-19/cpc/375-light.png`, `evidence/AT-19/cpc/375-dark.png`, `evidence/AT-19/cpc/768-light.png`, `evidence/AT-19/cpc/768-dark.png`, `evidence/AT-19/cpc/1280-light.png`, `evidence/AT-19/cpc/1280-dark.png`, `evidence/AT-19/cpc/state.txt`
Observation: The empty analyzer shows "Trade Analyzer", "Who gets what?", the teams row with Your Team, Team Two, and a "+" slot with "2 of 4", two empty cards, the line "Each team gives and gets at least one player.", and the "Grade the Trade" bar turned off (`disabled`). The shots were taken after the passphrase gate; on a first visit the gate covers the page.

## AT-20: The picker

App: site
Then: The sheet shows a tab for Team Two, a search field, and the chips All, QB, RB, WR, TE, and DEF. After Done, the Your Team card lists both players, each with a "from <Team Two>" tag.
Files: `evidence/AT-20/375-light-done.png`, `evidence/AT-20/375-light-sheet.png`, `evidence/AT-20/375-dark-done.png`, `evidence/AT-20/375-dark-sheet-with-two-tabs.png`, `evidence/AT-20/375-dark-sheet.png`, `evidence/AT-20/768-light-done.png`, `evidence/AT-20/768-light-sheet.png`, `evidence/AT-20/768-dark-done.png`, `evidence/AT-20/768-dark-sheet.png`, `evidence/AT-20/1280-light-done.png`, `evidence/AT-20/1280-light-sheet.png`, `evidence/AT-20/1280-dark-done.png`, `evidence/AT-20/1280-dark-sheet.png`, `evidence/AT-20/card-after-done.txt`, `evidence/AT-20/setup.txt`, `evidence/AT-20/tab-375-dark.txt`, `evidence/AT-20/tabs-three-teams.txt`
Observation: The open sheet shows a search field and the chips All, QB, RB, WR, TE, and DEF, but no visible tab for Team Two: the tablist holds a tab "Teehee" but has a height of 0, and with three teams the two tabs are also hidden (`tabs-three-teams.txt`, `375-dark-sheet-with-two-tabs.png`). After Done, the Your Team card lists Tee Higgins and Bhayshul Tuten, each with "from Teehee".

## AT-21: The sheet closes three ways

App: site
Then: Each action closes the sheet and keeps the picks.
Files: `evidence/AT-21/close-three-ways-375.webm`, `evidence/AT-21/setup.txt`, `evidence/AT-21/steps.txt`
Observation: `steps.txt` shows that Done, the close button, and a tap on the dim page each closed the sheet (no `[role=dialog]`), and each kept the checked player: after the three closes the card lists Tee Higgins, Bhayshul Tuten, and Tony Pollard. The recording shows the same sequence.

## AT-22: A third team

App: site
Then: The sheet shows every team, with the two teams in the trade dimmed. A third card shows with a remove button, and the slot reads "3 of 4".
Files: `evidence/AT-22/375-light-after.png`, `evidence/AT-22/375-light-sheet.png`, `evidence/AT-22/375-dark-after.png`, `evidence/AT-22/375-dark-sheet.png`, `evidence/AT-22/1280-light-after.png`, `evidence/AT-22/1280-light-sheet.png`, `evidence/AT-22/1280-dark-after.png`, `evidence/AT-22/1280-dark-sheet.png`, `evidence/AT-22/after.txt`, `evidence/AT-22/setup.txt`, `evidence/AT-22/sheet-rows.txt`
Observation: The "+" sheet lists all 12 teams, and Bo Girds and Teehee show "In the trade" at 0.4 opacity and `disabled`. After a tap on Lil Fridge, a third card "Team Three gets" shows with a remove button, and the slot reads "3 of 4".

## AT-23: The body of `POST /analyze` holds

App: site
Then: The request body has one `gives` entry for each side, with `to` set to the team of the card. It has the same shape as before the redesign.
Files: `evidence/AT-23/body-main.json.txt`, `evidence/AT-23/body-site-redesign.json.txt`, `evidence/AT-23/diff.txt`, `evidence/AT-23/setup.txt`
Observation: The body on this branch has one `gives` entry for each side, with `to` set to the other team (6 gives 8151 to 12, and 12 gives 6801 to 6). The body that `main` sends for the same trade is byte-identical (`diff.txt`, exit 0).

## AT-24: Loading and the result

App: site
Then: The form folds to a line of faces, the hero shows "Grading the Trade", and the bar reads "Grading…". Then the verdict fills the hero with the fairness block under it.
Files: `evidence/AT-24/375-light-loading.png`, `evidence/AT-24/375-light-result.png`, `evidence/AT-24/375-dark-loading.png`, `evidence/AT-24/375-dark-result.png`, `evidence/AT-24/768-light-loading.png`, `evidence/AT-24/768-light-result.png`, `evidence/AT-24/768-dark-loading.png`, `evidence/AT-24/768-dark-result.png`, `evidence/AT-24/1280-light-loading.png`, `evidence/AT-24/1280-light-result.png`, `evidence/AT-24/1280-dark-loading.png`, `evidence/AT-24/1280-dark-result.png`, `evidence/AT-24/result-text-1280-dark.txt`, `evidence/AT-24/setup.txt`
Observation: The loading shots show the form folded to one line with both team faces and "Kenneth Walker III for Tee Higgins", the hero with "GRADING THE TRADE", and the bar "Grading…". The result shots show the verdict "No" in the hero with the fairness block under it, "Lopsided: Bo Girds gives more."

## AT-25: The result of 3 teams

App: site
Then: The swap card shows one row for each team with "Gives" and "Gets", and each player shows a "TO" or "FROM" tag.
Files: `evidence/AT-25/375-light.png`, `evidence/AT-25/375-dark.png`, `evidence/AT-25/768-light.png`, `evidence/AT-25/768-dark.png`, `evidence/AT-25/1280-light.png`, `evidence/AT-25/1280-dark.png`, `evidence/AT-25/result-text-375-dark.txt`, `evidence/AT-25/setup.txt`
Observation: The swap card shows one row for each team: Teehee and Lil Fridge with "Gives" and "Gets", and Bo Girds with "You give" and "You get". Each player has a "TO" or "FROM" tag, such as "TO Lil Fridge" under Kenneth Walker III.

## AT-26: The error state

App: site
Then: The form unlocks, and a box with the alert icon, the message of `toErrorLine`, and "Try Again" sits above the bar.
Files: `evidence/AT-26/375-light.png`, `evidence/AT-26/375-dark.png`, `evidence/AT-26/1280-light.png`, `evidence/AT-26/1280-dark.png`, `evidence/AT-26/api-response.txt`, `evidence/AT-26/page-state.txt`, `evidence/AT-26/setup.txt`
Observation: The real API answered 422 `Caleb Williams is no longer on Bo Girds.` The page shows a box with the alert icon and that message above the bar, and both "Add a player" buttons are on. No "Try Again" button shows, because `toErrorLine` gives `retry: false` for a 422; the bar reads "Grade the Trade".

## AT-27: The finder on NorCal only

App: site
Then: Only NorCal shows the "Find a Trade" card under the form. Its result shows up to three cards, each with the swap, the Fairness pill, the reasons, and "See the Full Result".
Files: `evidence/AT-27/setup.txt`, `evidence/AT-27/cpc/375-light.png`, `evidence/AT-27/cpc/375-dark.png`, `evidence/AT-27/cpc/768-light.png`, `evidence/AT-27/cpc/768-dark.png`, `evidence/AT-27/cpc/1280-light.png`, `evidence/AT-27/cpc/1280-dark.png`, `evidence/AT-27/cpc/page-text.txt`
Observation: The CPC analyzer has no "Find a Trade" card at any width or theme, and the page text holds no "Find a Trade". This is the CPC half; the NorCal finder is in the NorCal entry.

## AT-28: The rankings Ladder

App: site
Then: The hero shows "01", All You Need Is Love, 11-5, up 4, and the tiles Playoff, Bye, and Seed. Under it come the week chips, one card for each other team, and the note on the four parts.
Files: `evidence/AT-28/cpc/375-light.png`, `evidence/AT-28/cpc/375-dark.png`, `evidence/AT-28/cpc/768-light.png`, `evidence/AT-28/cpc/768-dark.png`, `evidence/AT-28/cpc/1280-light.png`, `evidence/AT-28/cpc/1280-dark.png`
Observation: The hero shows "01", All You Need Is Love, "11-5", up 4, and the tiles Playoff 81%, Bye 33%, and Seed 1. Under it come the week chips 1 to 8, one card for each of the 11 other teams, and the note on the four parts. At 375 px the week chip 8 wraps to a second row.

## AT-29: A ranking card opens

App: site
Then: The card opens four tiles for Stand, Form, Sched, and Pts, the blurb, and a link to the manager page.
Files: `evidence/AT-29/375-light.png`, `evidence/AT-29/375-dark.png`, `evidence/AT-29/768-light.png`, `evidence/AT-29/768-dark.png`, `evidence/AT-29/1280-light.png`, `evidence/AT-29/1280-dark.png`, `evidence/AT-29/open-card.txt`
Observation: The card at rank 2, Teehee, opens with the tiles Stand 8, Form 2, Sched 2, and Pts 5, the blurb, and a "Manager page" link to `/2026/managers/12/`, with a red edge, at all three widths in both themes.

## AT-30: The managers index

App: site
Then: The index shows one card for each of the 12 teams in standings order, each with the grade box and the grade text. The tap opens that manager page.
Files: `evidence/AT-30/375-light.png`, `evidence/AT-30/375-dark.png`, `evidence/AT-30/768-light.png`, `evidence/AT-30/768-dark.png`, `evidence/AT-30/1280-light.png`, `evidence/AT-30/1280-dark.png`, `evidence/AT-30/cards.txt`, `evidence/AT-30/tap.txt`
Observation: The index shows 12 cards in standings order from All You Need Is Love 11-5 to NFC Least 3-13, each with a grade box and the grade text. A tap at the empty lower right of the Lil Fridge card hit the card link and opened `/2026/managers/3/`.

## AT-31: The manager page

App: site
Then: The page shows the back link, the hero with the grade letter as the big number and a W or L chip for each week, then Season So Far, Roster, Best Adds, Top Performers, and Moves. The name does not cut off.
Files: `evidence/AT-31/cpc/375-light.png`, `evidence/AT-31/cpc/375-dark.png`, `evidence/AT-31/cpc/768-light.png`, `evidence/AT-31/cpc/768-dark.png`, `evidence/AT-31/cpc/1280-light.png`, `evidence/AT-31/cpc/1280-dark.png`, `evidence/AT-31/cpc/structure.txt`
Observation: The page shows the back link "← All Managers", the hero with the grade "D" as the big letter and a W or L chip for weeks 1 to 8, then Season So Far, Roster, Best Adds, Top Performers, and Moves. The name wraps to two lines at 375 px and is not cut (`scrollWidth` is not more than `clientWidth`).

## AT-32: The 404 page

App: site
Then: The page shows the hero with "ERROR // PAGE NOT FOUND", a big "404", the line of the spec, and the buttons "Go to Week 8" and "Go Home".
Files: `evidence/AT-32/cpc/375-light.png`, `evidence/AT-32/cpc/375-dark.png`, `evidence/AT-32/cpc/768-light.png`, `evidence/AT-32/cpc/768-dark.png`, `evidence/AT-32/cpc/1280-light.png`, `evidence/AT-32/cpc/1280-dark.png`, `evidence/AT-32/cpc/text.txt`
Observation: The URL `/2026/week-99/` returns status 404 with `404.html` from the local server, and the page shows the hero with "ERROR // PAGE NOT FOUND", a big "404", the line "This page does not exist. The link may be old, or the week is not out yet.", and the buttons "Go to Week 8" and "Go Home". Each file shows the missing URL, not `/404.html`.

## AT-33: Photos and the fallback

App: site
Then: Each team row shows its Sleeper avatar. Each headshot sits in a round frame, cropped at the shoulders. A player with no headshot shows the initials in the frame.
Files: see the NorCal entry

## AT-34: The readability floor passes in CI

App: site
Then: The floor passes for both clients: the full floor on the 7 pages and the 3 open states, and the fast sweep on every other page. The output prints the count of each text tier and each exempt link.
Files: `evidence/AT-34/output.txt`
Observation: No CI run exists, because the Spec branch has no PR yet. A local run of `build-each-client.mjs` on 2026-11-05 at 17:26 passed in 37 s: the floor of CPC passed 58 tests and the floor of NorCal 56, with the full floor on 8 paths and 3 open states (the week strip, a recap, and a ranking card) and the fast sweep on the other pages. The output prints the prose and other text count of each page, and it prints no exempt link line.

## AT-35: The readability floor catches a break

App: site
Then: The floor fails and names the page, the element, and the size.
Files: `evidence/AT-35/output.txt`
Observation: With the hero blurb of the rankings page set to `text-[14px]`, the run stops at `The site check:floor of the client cpc failed.` with 8 failed tests. Each names the page, `cpc /rankings/`, the element `p.plate "All You Need Is Love climbs 4 places to "`, and the size: `is 14px, under the prose floor of 16px`.

## AT-36: The fonts load from the site

App: site
Then: The page loads exactly two font files from its own origin, 56,000 bytes or less in total, with two preloads. No request goes to an outside font host. The number columns stay aligned before the mono font loads.
Files: `evidence/AT-36/375-dark-fonts-blocked-standings.png`, `evidence/AT-36/375-dark-fonts-loaded-standings.png`, `evidence/AT-36/files-and-preloads.txt`, `evidence/AT-36/fonts-blocked-state.txt`, `evidence/AT-36/network-and-layout-shift.txt`
Observation: The week 8 page loads exactly two font files from `http://localhost:4173`, 31,340 and 22,320 bytes, 53,660 in total, with two `<link rel="preload" as="font">` tags and no request to an outside font host; the only other origin is the usage counter `gc.zgo.at`. The layout shift is 0 at 375 and 1280 px with the fonts, and 0 with the font files blocked, and the number columns of Standings stay aligned in the fallback fonts. The served export ran on a local Python server, not the Worker, so the cache headers of the Worker and the fallback on iOS and Android need a deploy and a device; they are not measured.

## AT-37: The brand schema rejects old keys

App: site
Then: The build fails and names the key or the missing set.
Files: `evidence/AT-37/fonts-key.txt`, `evidence/AT-37/one-set.txt`, `evidence/AT-37/radius-card-key.txt`
Observation: Each of the three builds fails with exit 1 and names the cause: `fonts: is not a known key`, `light.radius_card: is not a known key`, and `dark: is required`.

## AT-38: No waiver page

App: site
Then: No client builds a waiver page, and the URL shows the 404 page.
Files: `evidence/AT-38/cpc/375-dark.png`, `evidence/AT-38/cpc/routes.txt`
Observation: The CPC export has no waiver route: the only waiver file is the data file `2026/week-08/waiver.json`. The URL `/2026/week-08/waiver/` returns status 404 and the shot shows the 404 page.

## AT-39: The theme does not follow the system setting

App: site
Then: The page opens in dark.
Files: `evidence/AT-39/375-system-light.png`, `evidence/AT-39/state.txt`
Observation: With the system setting light (`prefers-color-scheme: light` matches) and no `cpc.theme` key, `<html>` has the `dark` class, the page background is rgb(20, 20, 20), and the 375 px shot shows the dark set.

## AT-40: The analyzer content holds

App: site
Then: The result shows "Suggested Counters · No counters yet.", and its text matches the text that `main` shows for the same trade.
Files: `evidence/AT-40/diff.txt`, `evidence/AT-40/setup.txt`, `evidence/AT-40/text-main.txt`, `evidence/AT-40/text-site-redesign.txt`
Observation: The result shows "SUGGESTED COUNTERS" and "No counters yet." on this branch and on `main`. The two texts are the same from the verdict to the end; the diff holds only the form part at the top (`main` keeps the full form, and this branch shows the folded line "Kenneth Walker III for Tee Higgins" with Edit) and one blank line.

## AT-41: The pipeline does not change

App: both
Then: No path under `apps/pipeline/`, `apps/api/`, or `clients/<slug>/published/` changes.
Files: `evidence/AT-41/output.txt`
Observation: The diff lists one path: `apps/pipeline/tests/test_client.py`, 2 insertions and 3 deletions. No path under `apps/api/` or `clients/<slug>/published/` changes. Brian accepted the change to `test_client.py` on ticket 04. No pipeline code changed.
