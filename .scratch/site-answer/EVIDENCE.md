# Site answer: evidence

Spec: `.scratch/site-answer/PRD.md`. Acceptance tests: `.scratch/site-answer/ACCEPTANCE.md`.
Built from: `9b603d8a`, on 2026-11-18. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 12 min for 13 site tests. The round output is `evidence/round.txt`. The norcal build of the first round stopped on a Next.js security notice, so AT-13 ran again alone. AT-5 and AT-14 ran again from `9b603d8a` in a second round of 2 min; its output is `evidence/round-2.txt`.
The local API ran with `make -C apps/api api-evidence` and called the live Jev. The files that no runner verb covers come from a Playwright script; see `evidence/extra-evidence-script.txt` and the `steps.txt` of each test.

## AT-1: "where is the trade analyzer" gets the card of the Trade Analyzer

App: both
Then: The page card shows the line "The Trade Analyzer has its own page.", the blurb "Grades a trade between two or more teams.", and the button "Open the Trade Analyzer", whose link is the Trade Analyzer link of the Menu.
Files: `evidence/AT-1/1280-dark.png`, `evidence/AT-1/1280-light.png`, `evidence/AT-1/375-dark.png`, `evidence/AT-1/375-light.png`, `evidence/AT-1/768-dark.png`, `evidence/AT-1/768-light.png`, `evidence/AT-1/ask-response.json`, `evidence/AT-1/menu-links.txt`, `evidence/AT-1/steps.json`, `evidence/AT-1/steps.txt`
Observation: Each shot shows the card with "The Trade Analyzer has its own page.", the blurb "Grades a trade between two or more teams.", and the button "Open the Trade Analyzer". `ask-response.json` holds `route: "site"` and `page: "analyzer"`, and the button href `/analyze/`; `menu-links.txt` shows the Menu item Trade Analyzer at `/analyze/`.

## AT-2: "what tools are there" gets the list view

App: both
Then: The lead line says "The site has 2 tools and 4 pages to read." The group "Tools" holds the Trade Analyzer and the Playoff Sim. The group "Pages to read" holds Week 10, Power Rankings, Managers, and Midseason Report. Each tile has its blurb, and no tile names Home, the egg board, or a past week.
Files: `evidence/AT-2/1280-dark.png`, `evidence/AT-2/1280-light.png`, `evidence/AT-2/375-dark.png`, `evidence/AT-2/375-light.png`, `evidence/AT-2/768-dark.png`, `evidence/AT-2/768-light.png`, `evidence/AT-2/ask-response.json`, `evidence/AT-2/steps.json`, `evidence/AT-2/steps.txt`
Observation: Each shot shows "The site has 2 tools and 4 pages to read.", the group TOOLS with Trade Analyzer and Playoff Sim, and the group PAGES TO READ with Week 10, Power Rankings, Managers, and Midseason Report, each with its blurb. `ask-response.json` holds `route: "site"` and `page: "all"`, and the six tile links hold no Home, egg board, or past week.

## AT-3: "what can this site do" gets the list view

App: both
Then: The same list view as AT-2 shows.
Files: `evidence/AT-3/1280-dark.png`, `evidence/AT-3/1280-light.png`, `evidence/AT-3/375-dark.png`, `evidence/AT-3/375-light.png`, `evidence/AT-3/768-dark.png`, `evidence/AT-3/768-light.png`, `evidence/AT-3/ask-response.json`, `evidence/AT-3/steps.json`, `evidence/AT-3/steps.txt`
Observation: Each shot shows the same list view as AT-2: the same lead line, the same two groups, and the same six tiles. `ask-response.json` holds `route: "site"` and `page: "all"`.

## AT-4: "how do I use the sim" gets the card of the Playoff Sim

App: both
Then: The page card of the Playoff Sim shows, with the blurb "Plays out the rest of the season, game by game." and the button link `/midseason/2026/#sim`. No step-by-step tutorial shows.
Files: `evidence/AT-4/1280-dark.png`, `evidence/AT-4/1280-light.png`, `evidence/AT-4/375-dark.png`, `evidence/AT-4/375-light.png`, `evidence/AT-4/768-dark.png`, `evidence/AT-4/768-light.png`, `evidence/AT-4/ask-response.json`, `evidence/AT-4/steps.json`, `evidence/AT-4/steps.txt`
Observation: Each shot shows the card of the Playoff Sim with "Plays out the rest of the season, game by game.", the button "Open the Playoff Sim", and the closed "All pages · 5" fold, with no tutorial steps. `ask-response.json` holds `route: "site"`, `page: "sim"`, and the button href `/midseason/2026/#sim`.

## AT-5: "take me to the weekly reports" gets the card of Week 10

App: both
Then: The page card of Week 10 shows, and its button links to the Week 10 link of the Menu.
Files: `evidence/AT-5/1280-dark.png`, `evidence/AT-5/1280-light.png`, `evidence/AT-5/375-dark.png`, `evidence/AT-5/375-light.png`, `evidence/AT-5/768-dark.png`, `evidence/AT-5/768-light.png`, `evidence/AT-5/ask-response.json`, `evidence/AT-5/menu-links.txt`, `evidence/AT-5/steps.json`, `evidence/AT-5/steps.txt`
Observation: Each shot shows the card of Week 10 with the lead "Week 10 has its own page." and the button "Open Week 10". `ask-response.json` holds `route: "site"`, `page: "week"`, and the button href `/2026/week-10/`, the href of the Menu item Week 10 in `menu-links.txt`.

## AT-6: A bare page name gets its card

App: both
Then: The page card of the Midseason Report shows.
Files: `evidence/AT-6/1280-dark.png`, `evidence/AT-6/1280-light.png`, `evidence/AT-6/375-dark.png`, `evidence/AT-6/375-light.png`, `evidence/AT-6/768-dark.png`, `evidence/AT-6/768-light.png`, `evidence/AT-6/ask-response.json`, `evidence/AT-6/steps.json`, `evidence/AT-6/steps.txt`
Observation: Each shot shows the card of the Midseason Report with the button "Open the Midseason Report". `ask-response.json` holds `route: "site"`, `page: "midseason"`, and the button href `/midseason/2026/`.

## AT-7: Casual typing gets the right card

App: both
Then: The page card of the Trade Analyzer shows.
Files: `evidence/AT-7/1280-dark.png`, `evidence/AT-7/1280-light.png`, `evidence/AT-7/375-dark.png`, `evidence/AT-7/375-light.png`, `evidence/AT-7/768-dark.png`, `evidence/AT-7/768-light.png`, `evidence/AT-7/ask-response.json`, `evidence/AT-7/steps.json`, `evidence/AT-7/steps.txt`
Observation: Each shot shows the card of the Trade Analyzer with the button "Open the Trade Analyzer". `ask-response.json` holds `route: "site"`, `page: "analyzer"`, and the button href `/analyze/`.

## AT-8: A page the client lacks gets the none case

App: both
Then: The card says "The site has no page for that. Here is what it has." and the rows of all 6 pages of CPC follow, open.
Files: `evidence/AT-8/1280-dark.png`, `evidence/AT-8/1280-light.png`, `evidence/AT-8/375-dark.png`, `evidence/AT-8/375-light.png`, `evidence/AT-8/768-dark.png`, `evidence/AT-8/768-light.png`, `evidence/AT-8/ask-response.json`, `evidence/AT-8/steps.json`, `evidence/AT-8/steps.txt`
Observation: Each shot shows "The site has no page for that. Here is what it has.", then six open rows: Week 10, Power Rankings, Managers, Trade Analyzer, Midseason Report, and Playoff Sim, with no fold. `ask-response.json` holds `route: "site"` and `page: "missing"`, and six row links.

## AT-9: The live route check holds the site questions and the traps

App: api
Then: At least 20 of the 22 site questions route to `site` with the right page key, each of the 18 traps stays off `site`, except that "show me the power rankings" may route to `site:rankings` (PRD item 6), and the old bar of the route eval still holds.
Files: `evidence/AT-9/live-run4.txt`, `evidence/AT-9/live-run5.txt`, `evidence/AT-9/live-run6.txt`, `evidence/AT-9/output.txt`
Observation: `output.txt` is one run of the command at cee7caf1: "Site hits: 22 of 22. Traps kept: 18 of 18. Traps on their expected route: 14 of 18.", the old part "Hits: 55 of 59" against its bar of 52, and "2 passed". Row 24, "show me the power rankings", routes to `site:rankings`. The earlier runs `live-run4.txt` to `live-run6.txt` each show "Site hits: 21 of 22. Traps kept: 18 of 18." and "2 passed".

## AT-10: Nothing moves to a page with no tap

App: site
Then: The address stays `/` for the 5 s, and only the tap opens the Trade Analyzer.
Files: `evidence/AT-10/375-light.webm`, `evidence/AT-10/address-log.txt`, `evidence/AT-10/steps.txt`
Observation: `address-log.txt` shows the address `http://127.0.0.1:4173/` at each 250 ms from 0.00 s to 4.79 s after the card showed, then the tap at 5.04 s, then `/analyze/` at 7.14 s. The recording `375-light.webm` holds a bar at the foot of the page with the live address, which reads `/` until the tap and `/analyze/` after it.

## AT-11: The "All pages" fold shows the other pages

App: site
Then: The rows of the other 5 pages of CPC show, each with its blurb and its link.
Files: `evidence/AT-11/closed-1280-dark.png`, `evidence/AT-11/closed-1280-light.png`, `evidence/AT-11/closed-375-dark.png`, `evidence/AT-11/closed-375-light.png`, `evidence/AT-11/closed-768-dark.png`, `evidence/AT-11/closed-768-light.png`, `evidence/AT-11/open-1280-dark.png`, `evidence/AT-11/open-1280-light.png`, `evidence/AT-11/open-375-dark.png`, `evidence/AT-11/open-375-light.png`, `evidence/AT-11/open-768-dark.png`, `evidence/AT-11/open-768-light.png`, `evidence/AT-11/steps.json`
Observation: The `closed-*` shots show the card with the fold "All pages · 5" shut. The `open-*` shots show the fold open, with the rows Week 10, Power Rankings, Managers, Midseason Report, and Playoff Sim, each with its blurb and a chevron link.

## AT-12: The Thread keeps a Site answer

App: site
Then: The same list view shows again, with the same links, and no new ask request goes to the API.
Files: `evidence/AT-12/after-375-dark.png`, `evidence/AT-12/after-375-light.png`, `evidence/AT-12/before-375-dark.png`, `evidence/AT-12/before-375-light.png`, `evidence/AT-12/network-log.txt`, `evidence/AT-12/steps.txt`
Observation: The `before-*` and `after-*` shots at 375 px show the same list view in each theme. `network-log.txt` shows the same six links before and after the reload in both themes, and 0 `POST .../ask` requests in the reload; the one API POST of the reload goes to `/clients/cpc/suggestions`.

## AT-13: NorCal shows only its own pages

App: both
Then: The list view holds only the pages of the NorCal Menu, plus its Midseason Report and Playoff Sim, and each link opens a NorCal page that exists.
Files: `evidence/AT-13/1280-dark.png`, `evidence/AT-13/1280-light.png`, `evidence/AT-13/375-dark.png`, `evidence/AT-13/375-light.png`, `evidence/AT-13/768-dark.png`, `evidence/AT-13/768-light.png`, `evidence/AT-13/ask-response.json`, `evidence/AT-13/links.txt`, `evidence/AT-13/steps.json`, `evidence/AT-13/steps.txt`
Observation: Each shot of the NorCal build shows the list view with Tools Trade Analyzer and Playoff Sim, and Pages to read Week 10, Power Rankings, Managers, and Midseason Report. `links.txt` shows status 200 for each of the six links on the NorCal export, each page title ending "NorCal Apex 6", and the NorCal Menu items Week 10, Power Rankings, Managers, and Trade Analyzer. `ask-response.json` shows the request to `/clients/norcal/ask` with `route: "site"` and `page: "all"`.

## AT-14: The Tool tone marks only a Tool

App: site
Then: In light, each Tool tile, Tool icon box, and "Open" button of a Tool has a red tint. In dark, each Tool tile is the raised surface with a rule, and each Tool icon box and "Open" button of a Tool has a red tint (PRD item 19). Each page to read, and the "Open" button of a page to read, has a plain surface with no red tint. No fill is solid white in dark, and no fill is solid black in light.
Files: `evidence/AT-14/1280-dark.png`, `evidence/AT-14/1280-light.png`, `evidence/AT-14/375-dark.png`, `evidence/AT-14/375-light.png`, `evidence/AT-14/768-dark.png`, `evidence/AT-14/768-light.png`, `evidence/AT-14/computed-backgrounds.json`, `evidence/AT-14/computed-backgrounds.txt`, `evidence/AT-14/measured-1280-dark.png`, `evidence/AT-14/measured-1280-light.png`, `evidence/AT-14/steps.json`, `evidence/AT-14/steps.txt`
Observation: `computed-backgrounds.txt` shows, in light: Tool tiles `rgb(248, 235, 234)`, Tool icon boxes and the "Open the Trade Analyzer" button `rgb(241, 214, 212)`, on the card `rgb(255, 255, 255)`. Read tiles are `rgb(255, 255, 255)` with a `1px solid rgb(224, 224, 224)` border, read icon boxes `rgb(235, 235, 235)`, and the "Open the Managers" button `rgb(244, 244, 244)`, the page fill. In dark: Tool tiles `rgb(38, 38, 38)`, the value of `--color-raised`, with a `1px solid rgb(51, 51, 51)` border, the value of `--color-rule`; Tool icon boxes and the Tool "Open" button `rgb(73, 41, 39)`. Read tiles are `rgb(31, 31, 31)`, read icon boxes `rgb(38, 38, 38)`, and the "Open the Managers" button `rgb(20, 20, 20)` on the card `rgb(31, 31, 31)`. No fill in dark is `rgb(255, 255, 255)` and no fill in light is `rgb(0, 0, 0)`; the `measured-1280-*` shots show the whole Thread that was measured.

## AT-15: Each tap target is at least 44 px tall

App: site
Then: Each one is at least 44 px tall.
Files: `evidence/AT-15/375-dark.png`, `evidence/AT-15/375-light.png`, `evidence/AT-15/heights.txt`, `evidence/AT-15/measured-375-light.png`, `evidence/AT-15/steps.json`, `evidence/AT-15/steps.txt`
Observation: `heights.txt` lists 19 targets at 375 px: the five fold rows of AT-1 and the six none rows of AT-8 at 67.7 px, the Tool tiles at 158.8 px, the read tiles at 156.5 px, and the "Open the Trade Analyzer" button and the "All pages · 5" button at 44 px. The smallest is 44 px.

## AT-16: Reduced motion keeps only the fades

App: site
Then: The tiles and the rows fade in, and nothing scales, rises, or blurs.
Files: `evidence/AT-16/375-reduced-off.webm`, `evidence/AT-16/375-reduced-on.webm`, `evidence/AT-16/motion-samples.txt`, `evidence/AT-16/steps.txt`
Observation: `motion-samples.txt` shows, with reduced motion on, only the transform `none` and the filter `none` on each tile and row over 2220 frames, with 61 opacity values. With reduced motion off, the same items show translate, scale from 0.96, and blur from 2px. The recordings `375-reduced-on.webm` and `375-reduced-off.webm` show both runs.

## AT-17: The Site answer names no internal part

App: site
Then: No string says "Jev", "Advisor", "Finder", "front door", or "rival".
Files: `evidence/AT-17/answer-text.txt`, `evidence/AT-17/code-search.txt`, `evidence/AT-17/steps.txt`
Observation: `answer-text.txt` holds the text and the labels of the three answers, and a count of 0 for each of the five words. `code-search.txt` finds no "Jev", "Advisor", or "rival" in the changed site code; "finder" shows only as a config field and a comment, and "front door" only in code comments.

## AT-18: A site route costs no Claude call and no cap

App: api
Then: The response has `route: "site"` and `page: "analyzer"`, no Claude call runs, the miss log has no new entry, and the count of each cap does not change.
Files: `evidence/AT-18/output.txt`
Observation: `output.txt` shows the command, "1 passed", and the source of the test and its fake Jev, for the test that sends one ask with the site Noul 0.9 and the page Choice `analyzer` and asserts `route: "site"`, `page: "analyzer"`, no Claude request, no miss, and the same cap counts.

## AT-19: A Menu link of the sim wins over the link of the midseason report

App: site
Then: The Playoff Sim tile links to that Menu link, not to `#sim` of the midseason report.
Files: `evidence/AT-19/output.txt`
Observation: `output.txt` shows the command, "1 passed", and the source of the test that gives the sim its own Menu link `/sim/2026/`, renders the list view, and asserts the Playoff Sim tile links to `/sim/2026/` and no link is `/midseason/2026/#sim`.

## AT-20: An unknown page key gets a 422

App: api
Then: The response is a 422, and no Jev request runs.
Files: `evidence/AT-20/output.txt`
Observation: `output.txt` shows the command, "1 passed", and the source of the test that sends `pages` with the key `casino` and asserts a 422 and no Jev request.

## AT-21: A kept key that the client no longer has shows the none case

App: site
Then: The none case shows, with the rows of the pages of CPC.
Files: `evidence/AT-21/output.txt`
Observation: `output.txt` shows the command, "1 passed" with exit 0 at `ca24c17a`, and the source of the test and its helpers. The test puts a kept Thread entry `{ kind: "site", page: "waiver" }` in `cpc.thread`, renders the page, and waits for the lead "The site has no page for that. Here is what it has." It then asserts that the "Pages" list holds the six links of the cpc pages, `/2026/week-08/` to `/midseason/2026/#sim`, that no "Open the" link shows, and that no ask request goes out.

## AT-22: Out of scope: the honest miss does not change

App: both
Then: The Answer says "I can't answer that." and shows no page link and no Site answer.
Files: `evidence/AT-22/1280-dark.png`, `evidence/AT-22/1280-light.png`, `evidence/AT-22/375-dark.png`, `evidence/AT-22/375-light.png`, `evidence/AT-22/768-dark.png`, `evidence/AT-22/768-light.png`, `evidence/AT-22/ask-response.json`, `evidence/AT-22/steps.json`, `evidence/AT-22/steps.txt`
Observation: `ask-response.json` holds `route: "miss"` and `page: null`, the answer text "I can't answer that." then CLOSEST TOPICS with Week recap, Your next matchup, and Start or sit, and an empty list of answer links. The shots show the same Answer, with no page link and no Site answer.
