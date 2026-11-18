# Site answer: acceptance tests

Spec: `.scratch/site-answer/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

## The setup of every test

- The CPC site is built from `clients/cpc/published/2026/`, latest week 10, with `front_door = true`, and served from the static export. The NorCal site is built from `clients/norcal/published/2026/`, latest week 10.
- The API runs on this machine with `make -C apps/api api-evidence`. It calls the real Jev. A test with a live Jev call records one run as its evidence.
- Your team is Lil Fridge, unless the Given names another team. The Thread starts empty.
- The pages of CPC and their links come from the Menu of the CPC build: Week 10, Power Rankings, Managers, and Trade Analyzer, plus the Midseason Report and the Playoff Sim at `/midseason/2026/#sim`.
- Site evidence is screenshots at 375, 768, and 1280 px, each in the light theme and the dark theme (ADR 0006), unless the test says otherwise.
- A test of motion adds a screen recording at 375 px.

## Tests

AT-1: "where is the trade analyzer" gets the card of the Trade Analyzer
App: both
Stories: 1, 10
Given: The CPC site and the API run.
When: The reader types "where is the trade analyzer" in the ask box and sends it.
Then: The page card shows the line "The Trade Analyzer has its own page.", the blurb "Grades a trade between two or more teams.", and the button "Open the Trade Analyzer", whose link is the Trade Analyzer link of the Menu.
Evidence: the ask response with `route: "site"` and `page: "analyzer"`, and screenshots of the card.

AT-2: "what tools are there" gets the list view
App: both
Stories: 2, 8, 9, 18
Given: The CPC site and the API run.
When: The reader types "what tools are there" and sends it.
Then: The lead line says "The site has 2 tools and 4 pages to read." The group "Tools" holds the Trade Analyzer and the Playoff Sim. The group "Pages to read" holds Week 10, Power Rankings, Managers, and Midseason Report. Each tile has its blurb, and no tile names Home, the egg board, or a past week.
Evidence: the ask response with `route: "site"` and `page: "all"`, and screenshots of the list view.

AT-3: "what can this site do" gets the list view
App: both
Stories: 3
Given: The CPC site and the API run.
When: The reader types "what can this site do" and sends it.
Then: The same list view as AT-2 shows.
Evidence: the ask response with `route: "site"` and `page: "all"`, and screenshots of the list view.

AT-4: "how do I use the sim" gets the card of the Playoff Sim
App: both
Stories: 4
Given: The CPC site and the API run.
When: The reader types "how do I use the sim" and sends it.
Then: The page card of the Playoff Sim shows, with the blurb "Plays out the rest of the season, game by game." and the button link `/midseason/2026/#sim`. No step-by-step tutorial shows.
Evidence: the ask response with `route: "site"` and `page: "sim"`, and screenshots of the card.

AT-5: "take me to the weekly reports" gets the card of Week 10
App: both
Stories: 5, 18
Given: The CPC site and the API run.
When: The reader types "take me to the weekly reports" and sends it.
Then: The page card of Week 10 shows, and its button links to the Week 10 link of the Menu.
Evidence: the ask response with `route: "site"` and `page: "week"`, and screenshots of the card.

AT-6: A bare page name gets its card
App: both
Stories: 6
Given: The CPC site and the API run.
When: The reader types "midseason report?" and sends it.
Then: The page card of the Midseason Report shows.
Evidence: the ask response with `route: "site"` and `page: "midseason"`, and screenshots of the card.

AT-7: Casual typing gets the right card
App: both
Stories: 7
Given: The CPC site and the API run.
When: The reader types "wheres the trade thing" and sends it.
Then: The page card of the Trade Analyzer shows.
Evidence: the ask response with `route: "site"` and `page: "analyzer"`, and screenshots of the card.

AT-8: A page the client lacks gets the none case
App: both
Stories: 12
Given: The CPC site and the API run. CPC has no waiver page.
When: The reader types "is there a waiver page" and sends it.
Then: The card says "The site has no page for that. Here is what it has." and the rows of all 6 pages of CPC follow, open.
Evidence: the ask response with `route: "site"` and `page: "missing"`, and screenshots of the card.

AT-9: The live route check holds the site questions and the traps
App: api
Stories: 7, 14, 15, 16, 28
Given: The fixture of route questions holds the 40 questions of decision 01, each with its expected route, and the pages of CPC.
When: The builder runs `pytest -m live -s` for the route eval in `apps/api`.
Then: At least 20 of the 22 site questions route to `site` with the right page key, each of the 18 traps stays off `site`, except that "show me the power rankings" may route to `site:rankings` (PRD item 6), and the old bar of the route eval still holds.
Evidence: the command and its full output, with the hit count of each part.

AT-10: Nothing moves to a page with no tap
App: site
Stories: 13
Given: The Site answer of AT-1 shows.
When: The reader waits 5 s, then taps "Open the Trade Analyzer".
Then: The address stays `/` for the 5 s, and only the tap opens the Trade Analyzer.
Evidence: a screen recording at 375 px with the address bar in view.

AT-11: The "All pages" fold shows the other pages
App: site
Stories: 11
Given: The Site answer of AT-1 shows.
When: The reader taps "All pages · 5".
Then: The rows of the other 5 pages of CPC show, each with its blurb and its link.
Evidence: screenshots at 375, 768, and 1280 px in both themes, with the fold closed and open.

AT-12: The Thread keeps a Site answer
App: site
Stories: 19
Given: The Site answer of AT-2 shows.
When: The reader reloads `/`.
Then: The same list view shows again, with the same links, and no new ask request goes to the API.
Evidence: screenshots at 375 px in both themes before and after the reload, and the network log of the reload.

AT-13: NorCal shows only its own pages
App: both
Stories: 17
Given: The NorCal site and the API run. Your team is a team of NorCal.
When: The reader types "what tools are there" and sends it.
Then: The list view holds only the pages of the NorCal Menu, plus its Midseason Report and Playoff Sim, and each link opens a NorCal page that exists.
Evidence: screenshots of the list view, and a list of each link with the status of its page in the static export.

AT-14: The Tool tone marks only a Tool
App: site
Stories: 8, 21, 22
Given: The Site answers of AT-1 and AT-2 show.
When: The reader views them in the light theme and in the dark theme.
Then: In light, each Tool tile, Tool icon box, and "Open" button of a Tool has a red tint. In dark, each Tool tile is the raised surface with a rule, and each Tool icon box and "Open" button of a Tool has a red tint (PRD item 19). Each page to read, and the "Open" button of a page to read, has a plain surface with no red tint. No fill is solid white in dark, and no fill is solid black in light.
Evidence: screenshots in both themes, and the computed background of each tile, icon box, and button from `getComputedStyle`.

AT-15: Each tap target is at least 44 px tall
App: site
Stories: 20
Given: The Site answers of AT-1, AT-2, and AT-8 show.
When: The reader measures each tile, row, and button at 375 px.
Then: Each one is at least 44 px tall.
Evidence: the measured height of each target from `getBoundingClientRect`, and a screenshot at 375 px.

AT-16: Reduced motion keeps only the fades
App: site
Stories: 23
Given: The browser sets `prefers-reduced-motion: reduce`.
When: The reader sends "what tools are there", then "where is the trade analyzer".
Then: The tiles and the rows fade in, and nothing scales, rises, or blurs.
Evidence: screen recordings at 375 px with reduced motion on and off.

AT-17: The Site answer names no internal part
App: site
Stories: 24
Given: The Site answers of AT-1, AT-2, and AT-8 show.
When: The reader reads each string of the three answers.
Then: No string says "Jev", "Advisor", "Finder", "front door", or "rival".
Evidence: the text of each answer from the page, and a search of the code of the Site answer for each word.

AT-18: A site route costs no Claude call and no cap
App: api
Stories: 25
Given: A pytest run of the API with the fake Jev of the port, whose site Noul is 0.9 and whose page Choice is `analyzer`.
When: The test sends one ask request.
Then: The response has `route: "site"` and `page: "analyzer"`, no Claude call runs, the miss log has no new entry, and the count of each cap does not change.
Evidence: the pytest command and its output.

AT-19: A Menu link of the sim wins over the link of the midseason report
App: site
Stories: 26, 27
Given: A Vitest run with a client whose Menu has its own link for the sim.
When: The test renders the list view.
Then: The Playoff Sim tile links to that Menu link, not to `#sim` of the midseason report.
Evidence: the Vitest command and its output.

AT-20: An unknown page key gets a 422
App: api
Stories: none
Given: A pytest run of the API.
When: The test sends an ask request whose `pages` holds the key `casino`.
Then: The response is a 422, and no Jev request runs.
Evidence: the pytest command and its output.

AT-21: A kept key that the client no longer has shows the none case
App: site
Stories: 19
Given: A Vitest run whose kept Thread holds a Site answer with the page key `waiver`, for CPC.
When: The test renders the Thread.
Then: The none case shows, with the rows of the pages of CPC.
Evidence: the Vitest command and its output.

AT-22: Out of scope: the honest miss does not change
App: both
Stories: none
Given: The CPC site and the API run.
When: The reader types "what's the weather" and sends it.
Then: The Answer says "I can't answer that." and shows no page link and no Site answer.
Evidence: the ask response with `route: "miss"`, and screenshots of the Answer.

## Trace

Story 1: AT-1
Story 2: AT-2
Story 3: AT-3
Story 4: AT-4
Story 5: AT-5
Story 6: AT-6
Story 7: AT-7, AT-9
Story 8: AT-2, AT-14
Story 9: AT-2
Story 10: AT-1
Story 11: AT-11
Story 12: AT-8
Story 13: AT-10
Story 14: AT-9
Story 15: AT-9
Story 16: AT-9
Story 17: AT-13
Story 18: AT-2, AT-5
Story 19: AT-12, AT-21
Story 20: AT-15
Story 21: AT-14
Story 22: AT-14
Story 23: AT-16
Story 24: AT-17
Story 25: AT-18
Story 26: AT-19
Story 27: AT-19
Story 28: AT-9
Out of scope "A step-by-step tutorial flow": AT-4
Out of scope "Page links in the honest miss": AT-22
Out of scope "A move to a page with no tap": AT-10
Out of scope "The solid white question bubble": no test. Reason: no ticket of this spec touches the bubble.
Out of scope "The standalone sim page": AT-19
Out of scope "Past weeks, the egg board, and the manager page of each other team": AT-2

## Revisions

None yet.
