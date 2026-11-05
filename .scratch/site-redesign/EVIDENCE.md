# Site redesign: evidence

Spec: `.scratch/site-redesign/PRD.md`. Acceptance tests: `.scratch/site-redesign/ACCEPTANCE.md`.
Built from: `12486d0e`, on 2026-11-05. The agent gives no Test verdict. Brian gives one for each test.

## Setup

Two agents recorded this evidence, one for each client. The tests with no client are in the CPC half.
A test of both clients keeps its CPC files under `cpc/` and its NorCal files under `norcal/`.

The NorCal half:

- Built from: `12486d0e`, on 2026-11-05, with `NEXT_PUBLIC_API_URL=http://localhost:8090 CLIENT=norcal pnpm --dir apps/site build`.
- The export ran on port 4174 and the local API on port 8090. See `evidence/AT-27/norcal/setup.txt`.
- The instrument is `agent-browser` 0.25.4. The recordings use Playwright 1.64.1 of the repo, because `agent-browser record` saved a 1280 px video at any viewport.
- Light screenshots set `cpc.theme` to `"light"`. Dark screenshots set it to `"dark"`. With no key, the site opens in dark.
- Each full-page screenshot ran a scroll pass first, so that each chapter shows. The fixed dock and the fixed analyzer bar show at the viewport height in a full-page screenshot, over the content under them.
- The agent gives no Test verdict. Brian gives one for each test.

The CPC half:

1. The CPC export: `NEXT_PUBLIC_API_URL=http://localhost:8080 CLIENT=cpc pnpm --dir apps/site build`.
2. The local API: `CORNERSTONE_ALLOWED_ORIGINS=http://localhost:4173 make -C apps/api api`, on port 8080.
3. The server: `python3 -m http.server 4173 --directory apps/site/out` first. From AT-32 on, a copy of it that answers a missing path with `404.html` and status 404, like the `404-page` handling of the Worker.
4. The instrument: `agent-browser` 0.25.4. The light theme sets `cpc.theme` to `"light"`. The dark theme removes the key, because dark is the default.
5. Before each full-page shot, the page scrolls to the end and back, so each chapter that rises on view shows. The dock is fixed, so a full-page shot shows it where the first screen ends.
6. A test of both clients keeps its CPC files under `cpc/`. A test with its own evidence list takes the widths and the themes of that list.
7. Round 1 rebuilt the CPC export from `feef43b4` with the same commands. Its instrument is Playwright 1.64.1 of the repo, in one script per group of tests. An init script or a reload sets the theme the same way. A full-page shot still runs the scroll pass first.

## AT-1: Dark is the first paint with no stored choice

App: site
Then: `<html>` has the class `dark` in the first paint, and the page shows the dark set with no light flash.
Files: `evidence/AT-1/cpc/375-dark.png`, `evidence/AT-1/cpc/first-load.webm`, `evidence/AT-1/cpc/served-html.txt`, `evidence/AT-1/norcal/served-html.txt`, `evidence/AT-1/norcal/375-dark.png`, `evidence/AT-1/norcal/first-load-375.webm`, `evidence/AT-1/norcal/first-frames-luma.txt`
Observation: CPC: The served HTML of the home page has `class="dark ..."` on `<html>`, and the boot script removes it only for a stored "light". The 375 px shot shows the dark set, and the 34 frames of the recording have a mean luma of 17.9 to 35.0 out of 255: blank black frames before the first paint, then the dark page, with no light frame. NorCal: The served HTML of the NorCal home page has `<html lang="en" class="dark ...">`, and a fresh browser with no `cpc.theme` key shows the dark set at 375 px. The first 12 frames of the recording have a mean luma of 33 to 42 of 255, with no light frame.

## AT-2: Dark with scripts off

App: site
Then: The page shows the dark set, and every chapter shows at rest.
Files: `evidence/AT-2/cpc/375-dark.png`, `evidence/AT-2/norcal/375-dark.png`
Observation: CPC: With scripts off (`--blink-settings=scriptEnabled=false`, and `window.__next_f` is undefined), `<html>` keeps the `dark` class. The full 375 px shot shows the dark set and every chapter from the hero to the Previous Week 7 link at rest. NorCal: With scripts off (`--blink-settings=scriptEnabled=false`, and `self.__next_f` undefined), the NorCal week 8 page shows the dark set, and every chapter from the hero to Next week shows at rest. The top band shows no theme button with scripts off.

## AT-3: A stored light choice opens in light

App: site
Then: The page opens in light with no dark flash, and `<html>` has no `dark` class.
Files: `evidence/AT-3/cpc/375-light.png`, `evidence/AT-3/cpc/load.webm`, `evidence/AT-3/cpc/state.txt`, `evidence/AT-3/norcal/375-light.png`, `evidence/AT-3/norcal/load-light-375.webm`, `evidence/AT-3/norcal/first-frames-luma.txt`
Observation: CPC: With `cpc.theme` set to "light", `<html>` has no `dark` class and the 375 px shot shows the light page and cards under the dark hero. In the recording, the first 4 frames are blank black frames before the first paint, and the next frame is already the light page (mean luma 137 or more); no dark page frame shows. NorCal: With `cpc.theme` set to `"light"` before the load, `<html>` has no `dark` class, and the home page opens with the light page and the dark hero. The first 12 frames have a mean luma of 127 to 130 of 255, with no dark frame.

## AT-4: NorCal has a light theme and the theme button

App: site
Then: The page goes light, with the NorCal light set of the spec: page `#f5f3ef`, white cards, and accent text `#9a3412`.
Files: `evidence/AT-4/norcal/375-before.png`, `evidence/AT-4/norcal/375-after.png`, `evidence/AT-4/norcal/768-before.png`, `evidence/AT-4/norcal/768-after.png`, `evidence/AT-4/norcal/1280-before.png`, `evidence/AT-4/norcal/1280-after.png`, `evidence/AT-4/norcal/colors.txt`
Observation: NorCal: A tap on the theme button in the top band turns the NorCal home page light at each width. After the tap, the computed page is `rgb(245, 243, 239)` (`#f5f3ef`), the cards are `rgb(255, 255, 255)`, and the accent text of "ALL 12 TEAMS" is `rgb(154, 52, 18)` (`#9a3412`).

## AT-5: The hero stays dark in light

App: site
Then: The hero sits on the `band` color with the grid, the brackets, and the glow. The page and the cards are light. NorCal gold shows only in the hero.
Files: `evidence/AT-5/cpc/375-light.png`, `evidence/AT-5/cpc/768-light.png`, `evidence/AT-5/cpc/1280-light.png`, `evidence/AT-5/norcal/375-light.png`, `evidence/AT-5/norcal/768-light.png`, `evidence/AT-5/norcal/1280-light.png`
Observation: CPC: At 375, 768, and 1280 px in light, the hero sits on the dark band with the grid, the corner brackets, and the red glow, and the page and the four tiles are light. This is the CPC half; NorCal gold is in the NorCal entry. NorCal: In light, the week 8 hero sits on a black band with the grid, the corner brackets, and a gold glow, and the page and the cards around it are light. Gold text shows only in the hero, as "CLOSEST FINISH · MARGIN".

## AT-6: The brand of each client

App: site
Then: CPC shows its red, its logo, and its copy. NorCal shows its gold and orange, its logo, and its copy. Both use Space Grotesk and JetBrains Mono.
Files: `evidence/AT-6/cpc/375-light.png`, `evidence/AT-6/cpc/375-dark.png`, `evidence/AT-6/cpc/768-light.png`, `evidence/AT-6/cpc/768-dark.png`, `evidence/AT-6/cpc/1280-light.png`, `evidence/AT-6/cpc/1280-dark.png`, `evidence/AT-6/cpc/fonts.txt`, `evidence/AT-6/norcal/375-light.png`, `evidence/AT-6/norcal/375-dark.png`, `evidence/AT-6/norcal/768-light.png`, `evidence/AT-6/norcal/768-dark.png`, `evidence/AT-6/norcal/1280-light.png`, `evidence/AT-6/norcal/1280-dark.png`, `evidence/AT-6/norcal/fonts.txt`
Observation: CPC: The home page shows the CPC red buttons and accents, the CPC logo, and the CPC copy "Cornerstone Fantasy Football League" in both themes. `fonts.txt` shows the heading in `spaceGrotesk`, the big number in `jetbrainsMono`, and both fonts loaded. These six files are copies of the AT-14 shots. NorCal: The NorCal home page shows gold accent text and orange buttons, with the copy "NorCal Apex 6" and "2026 // League Weekly". The masthead shows the site name as text and no logo, because `clients/norcal/brand.toml` says NorCal has no logo. The loaded fonts are `spaceGrotesk` and `jetbrainsMono`.

## AT-7: The hero and the motion

Round 1: built from feef43b4.

App: site
Then: The hero shows a scan line once. The content under it rises in a stagger, and the share bars grow once.
Files: `evidence/AT-7/cpc/load-1280.webm`, `evidence/AT-7/cpc/load-375.webm`, `evidence/AT-7/cpc/hero-frames-1280.png`, `evidence/AT-7/cpc/hero-frames-375.png`, `evidence/AT-7/cpc/cards-frames-1280.png`, `evidence/AT-7/cpc/cards-frames-375.png`, `evidence/AT-7/cpc/animations.txt`, `evidence/AT-7/norcal/load-375-dark.webm`, `evidence/AT-7/norcal/load-1280-dark.webm`
Observation: CPC: The hero crops at 1280 and 375 px show one thin light line that moves from the top of the hero to its foot between about 0.1 and 0.6 s, and `animations.txt` shows the `hero-scan` opacity at 0 from 1.6 s on, with no second pass. The hero content and the game cards fade and rise 8 px in. The share bars of the hero and of the game cards show at their full length in the first frame where they show: the fill widths stay 338, 197, and 194 px at 1280 px over the whole log, and no running animation changes the width or the scale of a bar fill. NorCal: In both recordings, the first frame shows a light line at the top edge of the empty hero, then the hero content fades and rises in over about 0.5 s, and the share bar under the two teams of the hero shows. The game cards with their share bars sit under the first screen, so the recordings do not show their growth.

## AT-8: Reduced motion

Round 1: built from feef43b4.

App: site
Then: No scan line, no rise, no bar growth, and no tap scale. All content shows at rest.
Files: `evidence/AT-8/load-and-tap-375.webm`, `evidence/AT-8/week-load-375.png`, `evidence/AT-8/rankings-load-375.png`, `evidence/AT-8/week-tap-frames.png`, `evidence/AT-8/rankings-tap-frames.png`, `evidence/AT-8/state.txt`
Observation: With reduced motion on, a tap on the Teehee game card and a tap on the Teehee ranking card each show the pressed card at its rest size (transform `none`, transition 0s, width 341 px while `:active`). Each recap or panel shows whole at opacity 1 and transform `none` from the first sample after the release, and no animation or transition event fires during the taps. In the first 104 ms of each load, before the page hydrates, the `reveal-safety` animation runs on the reveal boxes; the load shots show the page at rest.

## AT-9: The dock on a phone

App: site
Then: The dock stays at the bottom with Home, Week 8, Rankings, Managers, and Trade, each with an icon and a label. Week 8 is marked.
Files: `evidence/AT-9/cpc/375-light-end.png`, `evidence/AT-9/cpc/375-light-top.png`, `evidence/AT-9/cpc/375-dark-end.png`, `evidence/AT-9/cpc/375-dark-top.png`, `evidence/AT-9/cpc/dock.txt`, `evidence/AT-9/norcal/375-light-top.png`, `evidence/AT-9/norcal/375-light-end.png`, `evidence/AT-9/norcal/375-dark-top.png`, `evidence/AT-9/norcal/375-dark-end.png`
Observation: CPC: At 375 px the dock stays at the bottom both at the top and at the end of the week 8 page, with Home, Week 8, Rankings, Managers, and Trade, each with an icon and a label. Week 8 has `aria-current="page"` and a raised tile with a red mark in both themes. NorCal: At 375 px, the dock stays at the bottom at the top and at the end of the week 8 page, in both themes. It shows Home, Week 8, Rankings, Managers, and Trade, each with an icon and a label, and Week 8 is marked.

## AT-10: The pill bar on a desktop

Round 1: built from feef43b4.

App: site
Then: The top band shows the brand mark, the pill bar with full labels, the week chip, and the theme button. Rankings is marked, and the top band stays on screen.
Files: `evidence/AT-10/cpc/375-light-top.png`, `evidence/AT-10/cpc/375-light-scrolled.png`, `evidence/AT-10/cpc/375-dark-top.png`, `evidence/AT-10/cpc/375-dark-scrolled.png`, `evidence/AT-10/cpc/768-light-top.png`, `evidence/AT-10/cpc/768-light-scrolled.png`, `evidence/AT-10/cpc/768-dark-top.png`, `evidence/AT-10/cpc/768-dark-scrolled.png`, `evidence/AT-10/cpc/1024-light-top.png`, `evidence/AT-10/cpc/1024-light-scrolled.png`, `evidence/AT-10/cpc/1024-dark-top.png`, `evidence/AT-10/cpc/1024-dark-scrolled.png`, `evidence/AT-10/cpc/1280-light-top.png`, `evidence/AT-10/cpc/1280-light-scrolled.png`, `evidence/AT-10/cpc/1280-dark-top.png`, `evidence/AT-10/cpc/1280-dark-scrolled.png`, `evidence/AT-10/cpc/state.txt`, `evidence/AT-10/norcal/768-light-top.png`, `evidence/AT-10/norcal/768-light-scrolled.png`, `evidence/AT-10/norcal/768-dark-top.png`, `evidence/AT-10/norcal/768-dark-scrolled.png`, `evidence/AT-10/norcal/1280-light-top.png`, `evidence/AT-10/norcal/1280-light-scrolled.png`, `evidence/AT-10/norcal/1280-dark-top.png`, `evidence/AT-10/norcal/1280-dark-scrolled.png`
Observation: CPC: At every width the top band is one row of 61 px, `position: sticky` at top 0, and it stays on screen after a scroll of about 900 px. At 1024 and 1280 px the band shows the logo, the pill bar with the full labels Home, Week 8, Power Rankings, Managers, and Trade Analyzer, the WK 08 chip, and the theme button, and Power Rankings is marked. At 375 and 768 px the band shows the logo, the WK 08 chip, and the theme button, the pill bar does not show, and the dock at the foot marks Rankings. NorCal: The top band shows "NORCAL APEX 6", the pill bar with the full labels, the "WK 08" chip, and the theme button, and "Power Rankings" is marked. After the scroll to the end of the rankings page, the top band stays on screen. At 768 px the pill bar sits in a second row under the brand mark and the chip.

## AT-11: The week chip and the strip of weeks

Round 1: built from feef43b4.

App: site
Then: A strip shows weeks 6, 7, and 8, with the brand edge on week 8. A tap on week 7 opens the week 7 page.
Files: `evidence/AT-11/375-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/768-light.png`, `evidence/AT-11/768-dark.png`, `evidence/AT-11/1280-light.png`, `evidence/AT-11/1280-dark.png`, `evidence/AT-11/strip.txt`
Observation: A tap on WK 08 opens a strip with WK 06, WK 07, and WK 08 under the top band, and WK 08 has the red edge and `aria-current`. The band grows from 61 to 130 px, and at every width the strip ends at 129 px, above the page title at 164 px or lower. A tap on WK 07 opened `http://localhost:4173/2026/week-07/` with the title "Week 7 · Cornerstone Fantasy Football League".

## AT-12: The chapter rail

App: site
Then: The chapter rail on the left marks Standings.
Files: `evidence/AT-12/cpc/1280-light.png`, `evidence/AT-12/cpc/1280-dark.png`, `evidence/AT-12/cpc/marked.txt`, `evidence/AT-12/norcal/1280-light.png`, `evidence/AT-12/norcal/1280-dark.png`
Observation: CPC: At 1280 px with Standings at the top of the view, the chapter rail on the left marks STANDINGS in red in both themes, and `marked.txt` shows `aria-current="location"` on Standings. NorCal: At 1280 px with Standings at the top of the screen, the chapter rail on the left marks "STANDINGS" in the accent color, in both themes.

## AT-13: The client menu has no layout key

App: site
Then: Neither file has a `layout` key in `[menu]`, and a `layout` key fails the build with a message that names it.
Files: `evidence/AT-13/build-with-layout.txt`, `evidence/AT-13/menu-tables.txt`, `evidence/AT-13/norcal/menu.txt`, `evidence/AT-13/norcal/build-with-layout.txt`
Observation: CPC: Neither `client.toml` has a `layout` key: CPC lists its `[menu]` items only, and NorCal has no `[menu]` table. With `layout = "hamburger"` added by hand to CPC, the build fails with `menu.layout: is not a known key` and exit 1. NorCal: `clients/norcal/client.toml` has no `[menu]` table and no `layout` key. A temp copy of the NorCal client with `[menu]` and `layout = "tabs"` added fails the client build with "menu.layout: is not a known key", and no file of the repo changed.

## AT-14: The home page order

App: site
Then: The page shows, in order: the intro, the hero with "1.43" as the big number and a "Read Week 8" button, the four numbers, the top three of Power Rankings led by All You Need Is Love, the tool tiles, and a row for weeks 8, 7, and 6.
Files: `evidence/AT-14/375-light.png`, `evidence/AT-14/375-dark.png`, `evidence/AT-14/768-light.png`, `evidence/AT-14/768-dark.png`, `evidence/AT-14/1280-light.png`, `evidence/AT-14/1280-dark.png`, `evidence/AT-14/order.txt`
Observation: The full pages show, in order: the intro, the hero with "1.43" as the big number and a "Read Week 8" button, the four numbers, Power Rankings led by All You Need Is Love with 3 rows, the Tools tiles, and Weekly Reports rows for weeks 8, 7, and 6. The order is the same at all three widths in both themes.

## AT-15: The NorCal home page

App: site
Then: The hero shows "10.62" as the big number. Power Rankings is led by Mitseeker5000. One weekly report row shows, for week 8.
Files: `evidence/AT-15/norcal/375-light.png`, `evidence/AT-15/norcal/375-dark.png`, `evidence/AT-15/norcal/768-light.png`, `evidence/AT-15/norcal/768-dark.png`, `evidence/AT-15/norcal/1280-light.png`, `evidence/AT-15/norcal/1280-dark.png`
Observation: NorCal: The hero shows "10.62" as the big number, with kaiedmonds 132.38 over The Mean Machine 121.76. Power Rankings is led by Mitseeker5000, and Weekly Reports shows one row, for week 8. These files are copies of the AT-6 screenshots.

## AT-16: The week page order

Round 1: built from feef43b4.

App: site
Then: The page shows one scroll with no tabs, in order: the hero, the four numbers, every game, Game Changer with Joe Burrow at 42.48, Awards, Position leaders, Trades, the median game, Standings, Next week, and the footer.
Files: `evidence/AT-16/cpc/375-light.png`, `evidence/AT-16/cpc/375-dark.png`, `evidence/AT-16/cpc/768-light.png`, `evidence/AT-16/cpc/768-dark.png`, `evidence/AT-16/cpc/1280-light.png`, `evidence/AT-16/cpc/1280-dark.png`, `evidence/AT-16/cpc/headings.txt`, `evidence/AT-16/norcal/375-light.png`, `evidence/AT-16/norcal/375-dark.png`, `evidence/AT-16/norcal/768-light.png`, `evidence/AT-16/norcal/768-dark.png`, `evidence/AT-16/norcal/1280-light.png`, `evidence/AT-16/norcal/1280-dark.png`
Observation: CPC: The full pages show one scroll with no tab (`[role=tab]` count 0), in order: the hero, the four numbers, every game, Game Changer with Joe Burrow at 42.48, Awards, Position leaders, Trades, The median game, Standings, Next week, and the Previous Week 7 link. A scan of each word in `main` finds no tile or Awards label that breaks inside a word at 375, 768, or 1280 px; the one split word is "5-game" in Next week at 1280 px, which breaks after its hyphen. NorCal: The NorCal week 8 page is one scroll with no tabs: the hero, the four numbers, every game, Game Changer with D'Andre Swift at 27.9, Awards, Position leaders, Trades, Standings, and Next week. The page has no median game chapter and no `<footer>` element. At 375 and 768 px some Awards labels break inside a word, such as "UNDERPERF / ORMER" and "BENCHWARM / ER".

## AT-17: A recap opens on a tap

App: site
Then: The card opens its recap with a brand edge. The recap holds one "Manager page" link.
Files: `evidence/AT-17/cpc/375-light.png`, `evidence/AT-17/cpc/375-dark.png`, `evidence/AT-17/cpc/768-light.png`, `evidence/AT-17/cpc/768-dark.png`, `evidence/AT-17/cpc/1280-light.png`, `evidence/AT-17/cpc/1280-dark.png`, `evidence/AT-17/cpc/links.txt`
Observation: The tapped card of The Blue Tent and London Cooking opens its recap with a red edge in both themes at all three widths. The open card holds one link, "Manager page of The Blue Tent" to `/2026/managers/1/`.

## AT-18: Position leaders

Round 1: built from feef43b4.

App: site
Then: The chapter shows the top three WR of week 8.
Files: `evidence/AT-18/cpc/375-dark.png`, `evidence/AT-18/cpc/1280-dark.png`, `evidence/AT-18/cpc/rows.txt`
Observation: After a tap on WR, the WR chip shows as selected, and the chapter lists Tee Higgins 32.5, Ja'Marr Chase 25.6, and Michael Wilson 22.8. The text under the list changes from the quarterback line to "Teehee had the top receiver and the top running back, with Tee Higgins at 32.5 and Bhayshul Tuten at 28.9." At 1280 px the rail marks POSITION LEADERS before and after the tap.

## AT-19: The analyzer, empty

App: site
Then: The page shows "Trade Analyzer", "Who gets what?", the teams row with Your Team, Team Two, and a "+" slot with "2 of 4", two empty cards, the line on what each team needs, and the "Grade the Trade" bar turned off on the dock.
Files: `evidence/AT-19/cpc/375-light.png`, `evidence/AT-19/cpc/375-dark.png`, `evidence/AT-19/cpc/768-light.png`, `evidence/AT-19/cpc/768-dark.png`, `evidence/AT-19/cpc/1280-light.png`, `evidence/AT-19/cpc/1280-dark.png`, `evidence/AT-19/cpc/state.txt`, `evidence/AT-19/norcal/375-light.png`, `evidence/AT-19/norcal/375-dark.png`, `evidence/AT-19/norcal/768-light.png`, `evidence/AT-19/norcal/768-dark.png`, `evidence/AT-19/norcal/1280-light.png`, `evidence/AT-19/norcal/1280-dark.png`, `evidence/AT-19/norcal/setup.txt`
Observation: CPC: The empty analyzer shows "Trade Analyzer", "Who gets what?", the teams row with Your Team, Team Two, and a "+" slot with "2 of 4", two empty cards, the line "Each team gives and gets at least one player.", and the "Grade the Trade" bar turned off (`disabled`). The shots were taken after the passphrase gate; on a first visit the gate covers the page. NorCal: After the passphrase, the empty NorCal analyzer shows "Trade Analyzer", "Who gets what?", the teams row with Your Team, Team Two, a "+" slot, and "2 of 4", two empty cards, and "Each team gives and gets at least one player." The "Grade the Trade" bar is turned off above the dock.

## AT-20: The picker

Round 1: built from feef43b4.

App: site
Then: The sheet shows a tab for Team Two, a search field, and the chips All, QB, RB, WR, TE, and DEF. After Done, the Your Team card lists both players, each with a "from <Team Two>" tag.
Files: `evidence/AT-20/375-light-sheet.png`, `evidence/AT-20/375-light-done.png`, `evidence/AT-20/375-dark-sheet.png`, `evidence/AT-20/375-dark-done.png`, `evidence/AT-20/768-light-sheet.png`, `evidence/AT-20/768-light-done.png`, `evidence/AT-20/768-dark-sheet.png`, `evidence/AT-20/768-dark-done.png`, `evidence/AT-20/1280-light-sheet.png`, `evidence/AT-20/1280-light-done.png`, `evidence/AT-20/1280-dark-sheet.png`, `evidence/AT-20/1280-dark-done.png`, `evidence/AT-20/tabs-2-teams-375-dark.png`, `evidence/AT-20/tabs-3-teams-375-dark.png`, `evidence/AT-20/tabs-4-teams-375-dark.png`, `evidence/AT-20/tabs-2-teams-1280-dark.png`, `evidence/AT-20/tabs-3-teams-1280-dark.png`, `evidence/AT-20/tabs-4-teams-1280-dark.png`, `evidence/AT-20/state.txt`, `evidence/AT-20/setup.txt`
Observation: The open sheet shows a Teehee tab, the search field, and the chips All, QB, RB, WR, TE, and DEF at each width and theme. The tab row is 44 px high with 2, 3, and 4 teams at 375 and 1280 px, and each tab is 44 px high; at 375 px with 4 teams the third tab, All You Need Is Love, runs past the right edge of the sheet. After Done, the Your Team card lists Tee Higgins and Bhayshul Tuten, each with "from Teehee".

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

Round 1: built from feef43b4.

App: site
Then: The form unlocks, and a box with the alert icon, the message of `toErrorLine`, and "Try Again" sits above the bar.
Files: `evidence/AT-26/375-light.png`, `evidence/AT-26/375-dark.png`, `evidence/AT-26/1280-light.png`, `evidence/AT-26/1280-dark.png`, `evidence/AT-26/api-response.txt`, `evidence/AT-26/page-state.txt`, `evidence/AT-26/setup.txt`
Observation: The real API answered 422 `Caleb Williams is no longer on Bo Girds.` Each shot shows a box with the alert icon, that message, and an enabled "Try Again" button above the "Grade the Trade" bar, and both "Add a player" buttons are on. The first 1280 dark try got 429 from the rate limit, also with "Try Again"; a retake after 75 s got the 422 and replaced it.

## AT-27: The finder on NorCal only

App: site
Then: Only NorCal shows the "Find a Trade" card under the form. Its result shows up to three cards, each with the swap, the Fairness pill, the reasons, and "See the Full Result".
Files: `evidence/AT-27/setup.txt`, `evidence/AT-27/cpc/375-light.png`, `evidence/AT-27/cpc/375-dark.png`, `evidence/AT-27/cpc/768-light.png`, `evidence/AT-27/cpc/768-dark.png`, `evidence/AT-27/cpc/1280-light.png`, `evidence/AT-27/cpc/1280-dark.png`, `evidence/AT-27/cpc/page-text.txt`, `evidence/AT-27/norcal/375-light-result.png`, `evidence/AT-27/norcal/375-dark-result.png`, `evidence/AT-27/norcal/768-light-result.png`, `evidence/AT-27/norcal/768-dark-result.png`, `evidence/AT-27/norcal/1280-light-result.png`, `evidence/AT-27/norcal/1280-dark-result.png`, `evidence/AT-27/norcal/result-text.txt`, `evidence/AT-27/norcal/api-log.txt`, `evidence/AT-27/norcal/setup.txt`
Observation: CPC: The CPC analyzer has no "Find a Trade" card at any width or theme, and the page text holds no "Find a Trade". This is the CPC half; the NorCal finder is in the NorCal entry. NorCal: On NorCal the "Find a Trade" card shows under the form after Your Team is chosen. The result of one live `POST /clients/norcal/find` shows 2 cards, each with the swap, the Fairness pill "Good for both", the reasons of each side, and "See the Full Result". The CPC analyzer page belongs to the CPC half.

## AT-28: The rankings Ladder

Round 1: built from feef43b4.

App: site
Then: The hero shows "01", All You Need Is Love, 11-5, up 4, and the tiles Playoff, Bye, and Seed. Under it come the week chips, one card for each other team, and the note on the four parts.
Files: `evidence/AT-28/cpc/375-light.png`, `evidence/AT-28/cpc/375-dark.png`, `evidence/AT-28/cpc/768-light.png`, `evidence/AT-28/cpc/768-dark.png`, `evidence/AT-28/cpc/1280-light.png`, `evidence/AT-28/cpc/1280-dark.png`, `evidence/AT-28/cpc/chips.txt`, `evidence/AT-28/norcal/375-light.png`, `evidence/AT-28/norcal/375-dark.png`, `evidence/AT-28/norcal/768-light.png`, `evidence/AT-28/norcal/768-dark.png`, `evidence/AT-28/norcal/1280-light.png`, `evidence/AT-28/norcal/1280-dark.png`
Observation: CPC: The hero shows "01", All You Need Is Love, "11-5", up 4, and the tiles Playoff 81%, Bye 33%, and Seed 1. Under it come the week chips 1 to 8, one card for each of the 11 other teams, and the note on the four parts. The week chips sit on one row at 375, 768, and 1280 px; at 375 px the row scrolls sideways, and the shot shows chip 1 cut at the left edge with chip 8 in view. NorCal: The NorCal rankings hero shows "01", Mitseeker5000, "6-2 · –", and the tiles Playoff 97%, Bye 73%, and Seed 1. Under it come the week chips 1 to 8, one card for each of the other 11 teams, and the note on the four parts.

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
Files: `evidence/AT-31/cpc/375-light.png`, `evidence/AT-31/cpc/375-dark.png`, `evidence/AT-31/cpc/768-light.png`, `evidence/AT-31/cpc/768-dark.png`, `evidence/AT-31/cpc/1280-light.png`, `evidence/AT-31/cpc/1280-dark.png`, `evidence/AT-31/cpc/structure.txt`, `evidence/AT-31/norcal/375-light.png`, `evidence/AT-31/norcal/375-dark.png`, `evidence/AT-31/norcal/768-light.png`, `evidence/AT-31/norcal/768-dark.png`, `evidence/AT-31/norcal/1280-light.png`, `evidence/AT-31/norcal/1280-dark.png`
Observation: CPC: The page shows the back link "← All Managers", the hero with the grade "D" as the big letter and a W or L chip for weeks 1 to 8, then Season So Far, Roster, Best Adds, Top Performers, and Moves. The name wraps to two lines at 375 px and is not cut (`scrollWidth` is not more than `clientWidth`). NorCal: The page of The Mean Machine shows the "All Managers" back link, the hero with the grade "D" as the big letter and a W or L chip for weeks 1 to 8, then Season So Far, Roster, Best Adds, Top Performers, and Moves. The name wraps to two lines at 375 px and does not cut off.

## AT-32: The 404 page

App: site
Then: The page shows the hero with "ERROR // PAGE NOT FOUND", a big "404", the line of the spec, and the buttons "Go to Week 8" and "Go Home".
Files: `evidence/AT-32/cpc/375-light.png`, `evidence/AT-32/cpc/375-dark.png`, `evidence/AT-32/cpc/768-light.png`, `evidence/AT-32/cpc/768-dark.png`, `evidence/AT-32/cpc/1280-light.png`, `evidence/AT-32/cpc/1280-dark.png`, `evidence/AT-32/cpc/text.txt`, `evidence/AT-32/norcal/375-light.png`, `evidence/AT-32/norcal/375-dark.png`, `evidence/AT-32/norcal/768-light.png`, `evidence/AT-32/norcal/768-dark.png`, `evidence/AT-32/norcal/1280-light.png`, `evidence/AT-32/norcal/1280-dark.png`
Observation: CPC: The URL `/2026/week-99/` returns status 404 with `404.html` from the local server, and the page shows the hero with "ERROR // PAGE NOT FOUND", a big "404", the line "This page does not exist. The link may be old, or the week is not out yet.", and the buttons "Go to Week 8" and "Go Home". Each file shows the missing URL, not `/404.html`. NorCal: The NorCal 404 page shows the hero with "ERROR // PAGE NOT FOUND", a big "404", "This page does not exist. The link may be old, or the week is not out yet.", and the buttons "Go to Week 8" and "Go Home". The files show `/404.html`, because `python3 -m http.server` answers `/2026/week-99/` with its own 404 text and does not serve `404.html`.

## AT-33: Photos and the fallback

App: site
Then: Each team row shows its Sleeper avatar. Each headshot sits in a round frame, cropped at the shoulders. A player with no headshot shows the initials in the frame.
Files: `evidence/AT-33/norcal/375-light-hero.png`, `evidence/AT-33/norcal/375-dark-hero.png`, `evidence/AT-33/norcal/375-light-awards.png`, `evidence/AT-33/norcal/375-dark-awards.png`, `evidence/AT-33/norcal/375-light-position-leaders.png`, `evidence/AT-33/norcal/375-dark-position-leaders.png`
Observation: NorCal: Each team row shows its Sleeper avatar, and VarsityBlue2 shows a plain light circle. Each headshot in Awards and Position leaders sits in a round frame, cropped at the shoulders. The one player with initials is Chuba Hubbard, "CH" in the hero; Awards and the QB, RB, WR, and TE chips of Position leaders show no initials.

## AT-34: The readability floor passes in CI

Round 1: built from feef43b4.

App: site
Then: The floor passes for both clients: the full floor on the 7 pages and the 3 open states, and the fast sweep on every other page. The output prints the count of each text tier and each exempt link.
Files: `evidence/AT-34/ci-floor.txt`, `evidence/AT-34/local-check.txt`
Observation: CI run 42122278427 of `Check` on PR #11 passed on 605c4532, before the round 1 fixes: the floor of CPC ran from 22:35:05 to 22:35:41 UTC with 58 tests, and the floor of NorCal from 22:35:47 to 22:36:18 UTC with 56 tests, with the full floor on 8 pages and 3 open states, and its output prints no exempt-link line. The local `pnpm --dir apps/site check` on feef43b4 passed in 52 s: CPC 68 tests and NorCal 66, with the full floor on 7 pages (`/`, `/2026/managers/`, one manager page, `/2026/week-08/`, `/404-floor-check/`, `/analyze/`, `/rankings/`) and 3 open states (the week strip, a recap, a ranking card), and the fast sweep on 13 other pages of CPC and 11 of NorCal. Each of the 80 full-floor cases prints a prose and other text count and the line "exempt links inside prose: none".

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
Files: `evidence/AT-38/cpc/375-dark.png`, `evidence/AT-38/cpc/routes.txt`, `evidence/AT-38/norcal/routes.txt`, `evidence/AT-38/norcal/375-url.png`
Observation: CPC: The CPC export has no waiver route: the only waiver file is the data file `2026/week-08/waiver.json`. The URL `/2026/week-08/waiver/` returns status 404 and the shot shows the 404 page. NorCal: The NorCal export holds no waiver route and no waiver HTML page; `out/2026/week-08/` holds only the data file `waiver.json`. The server answers `/2026/week-08/waiver/` with 404, and the screenshot shows the plain 404 text of `python3 -m http.server`, not the 404 page of the site.

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
