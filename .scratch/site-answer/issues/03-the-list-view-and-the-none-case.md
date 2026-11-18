# 03: The list view and the none case

Spec: `.scratch/site-answer/PRD.md`. Acceptance tests AT-2, AT-3, AT-8, AT-13, AT-14, AT-15, AT-16, AT-17, AT-22.

**App:** site

**What to build:** A manager asks "what tools are there" and gets the list view: the lead line, then the groups "Tools" and "Pages to read" as the A launcher of decision 02, with the pop-in of the tiles. A question about a page the client lacks gets the none case: the lead line "The site has no page for that. Here is what it has." and the open rows of all the pages. NorCal shows only its own pages. An honest miss shows no Site answer.

**Blocked by:** 02.

**Status:** ready-for-agent

- [x] "what tools are there" and "what can this site do" show the list view of CPC with 2 Tools and 4 pages to read (AT-2, AT-3).
- [x] "is there a waiver page" shows the none case with the 6 pages of CPC (AT-8).
- [x] The list view of NorCal holds only NorCal pages, and each link opens a page that exists (AT-13).
- [ ] The list view and the none case have the Tool tone, 44 px targets, fades only with reduced motion, and no internal name (AT-14, AT-15, AT-16, AT-17, list half).
- [x] "what's the weather" shows "I can't answer that." and no Site answer (AT-22, site half).
