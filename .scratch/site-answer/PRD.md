# Site answer: the chat points a manager to each page and tool of the site

Status: ready-for-agent
Date: 2026-11-18
Apps: site and api. The api routes a question about the site and picks the page that it asks about. The site builds the Site answer from its own Menu and shows it in the Thread. The pipeline does not change.
Spec branch: `site-answer`.
Source: the map `.scratch/site-answer/MAP.md` and decision tickets 01 to 03. The grill and the prototypes of 2026-11-18. ADR 0015, ADR 0021, ADR 0024, ADR 0036.
Tickets: 01 to 03, in `issues/`.

## Problem Statement

A manager types "where is the trade analyzer" or "what tools are there" into the ask box. The chat answers "I can't answer that." It knows the league, but it does not know the site.

Today the route gives these questions a miss or a wrong Answer. "where is the trade analyzer" and "what tools are there" are an honest miss. "take me to the weekly reports" opens the week recap. "what can this site do" goes to a free answer, which has no page link. So a manager who asks the chat for a page does not get the page.

## Solution

The chat gives a Site answer to a question about the site itself. The Site answer has two displays:

1. **The list view.** It answers "what tools are there" or "what can this site do". A lead line sits on the Thread. Two groups of tiles follow, "Tools" and "Pages to read". Each tile links to its page.
2. **The page card.** It answers "where is the trade analyzer" or "how do I use the sim". The normal Answer card shows the page, a one-line blurb of what it does, and one "Open" button. An "All pages" fold holds the rest.

A question about a page that the client does not have, such as "is there a waiver page", gets the page card with no page. One line says that the site has no such page, and the rows of all the pages follow.

A soft red Tool tone marks a Tool in both themes. Nothing moves to a page with no tap. A Site answer costs no Claude call and uses no cap.

## User Stories

1. As a manager, I want to ask "where is the trade analyzer", so that I get a link to it.
2. As a manager, I want to ask "what tools are there", so that I see each Tool and each page of the site at once.
3. As a manager, I want to ask "what can this site do", so that I learn what the site offers.
4. As a manager, I want to ask "how do I use the sim", so that I learn what the sim does and get a link to it.
5. As a manager, I want to ask "take me to the weekly reports", so that I get a link to the week page.
6. As a manager, I want to type a page name alone, such as "midseason report?" or "analyzer", so that I get its card.
7. As a manager, I want casual phone typing, such as "wheres the trade thing", to work, so that I do not need exact names.
8. As a manager, I want each Tool to read apart from the pages to read, so that I find the analyzer and the sim fast.
9. As a manager, I want a one-line blurb on each page, so that I know what each page holds before I open it.
10. As a manager, I want one clear "Open" button on the page card, so that I reach the page in one tap.
11. As a manager, I want the other pages in a fold under the card, so that the card stays short and the rest is one tap away.
12. As a manager, I want to ask for a page the site does not have, so that I learn it does not exist and see what does.
13. As a manager, I want the chat never to move me to a page by itself, so that a wrong guess does not take me away from the Thread.
14. As a manager, I want "where is my team in the standings" to keep its league answer, so that a "where is" question about the league is not sent to a page list.
15. As a manager, I want "show me the power rankings" to get the rankings page, as a Topic Answer or as a Site answer, so that I reach the rankings either way.
16. As a manager, I want "how do i set my lineup" to keep its old route, so that a question about Sleeper does not get a page of this site.
17. As a manager, I want the Site answer to show only the pages of my league, so that each link works.
18. As a manager, I want the Week tile to name the latest week, so that I know which week the link opens.
19. As a manager, I want the Site answer to stay in the Thread after a reload, like each other Answer, so that I can tap the link later.
20. As a manager on a phone, I want each tile and button to be at least 44 px, so that I can tap it with one thumb.
21. As a manager in the dark theme, I want no solid white blocks, so that the Site answer does not glare.
22. As a manager in the light theme, I want no solid black blocks, so that the Tools look like the rest of the light page.
23. As a manager who turns on reduced motion, I want only fades, so that the Site answer does not move on screen.
24. As a manager, I want the Site answer to name no internal part, such as a model or a code name, so that the site reads as one product.
25. As the commissioner, I want a Site answer to cost no Claude call and no cap, so that a page question is free.
26. As the commissioner, I want a new page with a Menu link to show up in the Site answer on its own, so that no copy goes stale.
27. As the commissioner, I want the standalone sim page of the season sim to replace the sim link of the midseason report when it gets a Menu link, so that the sim Tool always opens the best page.
28. As the commissioner, I want the live route check to cover the site questions and the traps, so that a later change of the route cannot break them unseen.

## Implementation Decisions

**The route, in the api.**

1. The ask request gets a new field, `pages`. It is the list of the pages of the client, from the site: each with its key and one line about the page. The api does not read the client files. The site owns the Menu, so one source holds the page list.
2. The key of a page is a package name of the site, such as `week`, `rankings`, `managers`, `analyzer`, `midseason`, or `sim`. The api rejects an unknown key and a list of more than 12 pages with a 422.
3. The Jev state of the route gets a `site_pages` field from `pages`, with each key and its line. This is the field of decision 01.
4. The Jev request of the route gets one new Noul and one new Choice. Both share the one request of today.
   - The Noul, `n5` of decision 01: "Does `manager_question` ask for a page or tool of the site, by its name or by what it does?" Yes: "The manager names a page or tool in `site_pages` as the thing they want, or asks where one is, which ones the site has, or how to use one." No: "The manager asks for a fact, a judgment, or advice about the league or its teams, or asks for something unrelated to the site."
   - The Choice, `c1` of decision 01: "Which page in `site_pages` does the manager ask about in `manager_question`?" Its options are each key of `site_pages`, plus two more:
     - `all`: "No one page: the manager asks about the whole site, or which pages or tools it has."
     - `missing`: "A page or tool that is not in `site_pages`."
   - Decision 01 used one `none` option for both. The spec splits it in two, so the site can tell the list view from the none case with no second request. The live route check proves the split.
5. The route table of `decide()` gets one new row, after `ABUSE` and before every other row: a yes above 0.7 on the new Noul gives the route kind `site`. An unsure or a no falls through to the old table, unchanged. This is order A of decision 01.
6. A bare page name that is also a Topic keeps its Topic with no extra rule. Decision 01 measured "show me the power rankings" at 0.70 and "power rankings?" at 0.56 on `n5`. The live eval of ticket 01 measured them at 0.78 to 0.83 and 0.58 to 0.70. So "show me the power rankings" gets the Site answer, and "power rankings?" keeps its Topic. When a question scores above 0.7, the Site answer still links to the same page. That is acceptable, so no code guards it. This settles item 5 of ticket 03.
7. The ask response of a `site` route holds the new field `page`: the key of the top Choice, `all`, or `missing`. The fields `topic`, `team`, `closest`, and `suggestion` are null or empty for it.
8. A `site` route writes no entry in the miss log, makes no Claude call, and does not touch a cap.

**The Site answer, in the site.**

9. The site builds the page list from the Menu that the shell shows to the client, with `menuPages()` and the same menu links:
   - It takes each Menu item except Home.
   - It adds the midseason report when the client has the package `midseason` and the Menu lacks it.
   - It adds the sim as a Tool when the client has the packages `sim` and `midseason`. Its link is the sim section of the midseason report, `#sim`. When the sim gets a Menu link of its own, that link wins.
   - The client `front_door` flag picks `front_door_items` or `items` as the Menu does today. So a client with the flag off gets its own Menu in the list. That settles item 3 of ticket 03.
10. A page is a Tool when its package marks it as one. The packages `analyzer` and `sim` are Tools. Each other package is a page to read, including `managers` (decision 02, Brian's answer on the glossary).
11. Each package that can show in the list gives a fixed blurb of one line beside its menu link. Code writes each blurb. Claude never writes one. Both clients share the blurbs, so they live with the package, not in `copy.toml`. This settles item 2 of ticket 03. The blurbs:
    - `analyzer`: "Grades a trade between two or more teams."
    - `sim`: "Plays out the rest of the season, game by game." The blurb does not say "playoff odds", because those words lifted the trap "where are the playoff odds" to `site` in the live eval.
    - `week`: "The recap, scores, and awards of the week."
    - `rankings`: "Every team ranked, with the weekly moves."
    - `managers`: "Each manager, with the grades of the season."
    - `midseason`: "The midseason awards, grades, and roasts."
12. The `pages` field of the ask request sends each key with its label and blurb. The Week label is "Week N" of the latest week, as in the Menu.
13. `itemOfRoute` maps the route `site` to a new Thread item `{ kind: "site"; question; page }`. The Thread store keeps it like each other item. The item holds only the key. The site builds the links at render time from the Menu of the build, so a kept Site answer never holds an old link. This settles item 4 of ticket 03.
14. The display follows the `page` value:
    - `all` gives the list view.
    - A page key gives the page card of that page.
    - `missing` gives the none case.
    - A key that the client no longer has, such as in a kept Thread after a Menu change, gives the none case.
15. The lead lines, fixed in code. These settle item 1 of ticket 03:
    - The list view: "The site has N tools and M pages to read." With one Tool, the line says "1 tool".
    - The page card: "The <label> has its own page."
    - The none case: "The site has no page for that. Here is what it has."
16. The list view is the A launcher of decision 02:
    - Two groups, "Tools" and "Pages to read", each a grid of tiles.
    - The Tools take 2 columns. The pages to read take 2 columns, or 3 from 640 px.
    - The whole tile is the link, with an arrow mark in its corner. A tile holds an icon box, the label, and the blurb.
    - The tiles pop in from scale 0.96 with a fade, 250 ms, 40 ms apart.
17. The page card is the B card of decision 02:
    - The normal Answer card holds the lead line, the icon box with the page name, and the blurb.
    - One full-width "Open the <label>" button follows, and an "All pages · N" fold holds the other pages as rows.
    - No "Menu · <label>" line shows.
    - The card settles as a normal Answer does. The rows rise 8 px with a 2 px blur, 40 ms apart.
18. The none case is the B card with no page: the lead line, then the rows of all the pages, open.
19. The Tool tone of decision 02 marks a Tool in both themes. Red marks only a Tool. The pages to read keep the plain card surface.
    - Tool tile: `color-mix(in srgb, var(--color-accent) 10%, var(--color-card))` in light. `bg-raised` with a `border-rule` in dark.
    - Icon box of a Tool and the "Open" button of a Tool: `color-mix(in srgb, var(--color-accent) 20%, var(--color-card))` in light. 24% into `var(--color-raised)` in dark. Text and icon in `--color-accent-ink`.
    - Hover: 28% in light and 34% in dark, over 150 ms with `ease-out`. The light Tool tile gets the same hover. Press: the `press` utility.
    - No solid white fill in dark. No solid black fill in light.
20. Each tile, row, and button is a real `<a href>`, at least 44 px tall. Reduced motion keeps only the fades. No code moves to a page with no tap.
21. The copy names no internal part: no "Jev", "Advisor", "Finder", or "front door". It never says "rival". No code names the bare word `plate` (ADR 0036). The prototype used `iconBox`.
22. The site uses `ui-sdk` for the fold, and the motion tokens of `transitions-dev`, per the design bar.

## Testing Decisions

A good test checks what a manager or a caller sees: the route of a question, the response of the ask route, the Answer in the Thread, and its links. It does not check a private function or a class name.

The seams, from high to low. Each one exists today.

1. **The live route eval, `pytest -m live`.** Prior art: the AT-17 eval of the route and its fixture of route questions. The fixture gets the 40 questions of decision 01, with a new expect of the shape `site:<key>`, `site:all`, or `site:missing`. The bar holds two parts:
   - At least 20 of the 22 site questions route to `site`. Each one that routes to `site` picks the right key.
   - Each of the 18 traps stays off `site`. The one exception is "show me the power rankings", which may route to `site:rankings` by item 6. The old bar of AT-17 still holds with `pages` in the state.
2. **The ask route of the api, with the one fake Jev of the port (ADR 0015).** Prior art: `test_ask.py`. It checks the new row of `decide()`, the `page` field, the 422 on a bad key, and no miss log entry, Claude call, or cap for a `site` route.
3. **The page of the front door in the site, with Vitest.** Prior art: `page-ask.test.tsx` and `page-free.test.tsx`. A fake ask response of each `page` value renders the list view, the page card, and the none case with the real Menu of each client. It checks each link, the groups, the lead line, the kept Thread after a reload, and a key that the client lacks.
4. **Screenshots on a phone width, in both themes.** Prior art: the evidence of the front door. They show the Tool tone, no solid white in dark, and no solid black in light.

No test adds a mock. The api tests use the fake Jev of the port. The site tests use a fake response at the fetch seam, as the front door tests do today.

## Out of Scope

- A step-by-step tutorial flow for each Tool. It needs content of its own. Brian chose to skip it for now. A later spec can start it with `4ag:plan`.
- Page links in the honest miss. A miss says only "I can't answer that."
- A move to a page with no tap.
- The solid white question bubble of the Thread in the dark theme. It is a Quick win in the queue.
- The standalone sim page. The feature `season-sim` owns it. This spec only lets its Menu link win.
- Past weeks, the egg board, and the manager page of each other team in the list.

## Further Notes

- The new questions grow one route request from 2894 to about 3450 input tokens, by decision 01. Jev is the cheap part of the cost (front-door decision 03).
- The `pages` field moved the old route of 5 of 40 questions in decision 01. Four were site questions that the new row catches first. The fifth, "who won the midseason awards", moved from a miss to a free answer, which is a better route. The live eval guards the rest.
- The split of the `none` option into `all` and `missing` is new in the spec and was not run in decision 01. The live eval proves it. If it fails, the fallback is one `none` option that gives the list view.
- The prototype of decision 02 sits on the branch `site-answer-proto-02` at `fc6714e9`. It never merges. Read it for the class sets of the Tool tone, not for its structure.
