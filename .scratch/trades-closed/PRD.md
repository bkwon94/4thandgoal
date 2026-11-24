# Trades closed

Status: ready-for-agent
Date: 2026-11-24
Apps: site and API. The site build leaves out each trade tool of a client after its Lock, and writes a closed page at `/analyze/`. The API refuses each trade route of a client after its Lock, and the fair warm-up skips the client. The pipeline does not change.
Spec branch: `trades-closed`.
Source: the session of 2026-11-24, questions Q1 to Q10 of `4ag:plan`. No map and no decision tickets: Brian confirmed that the feature has no fog. ADR 0037 (ui-sdk standard) holds for the closed page.
Tickets: 01 to 04, in `issues/`.

## Problem Statement

The CPC trade deadline passed at the Lock, 00:00 Eastern on 2026-11-24. Sleeper now refuses each CPC trade. The site still offers the trade analyzer, the Finder, the trade Topics of the front door, and the Deadline banner. A manager can still grade a trade or ask for trade ideas that no one can send. Each such call also spends Claude and TypeSafe money for nothing.

NorCal has a later deadline, after week 14. Its trade tools must stay open until then, and close at its own Lock with no hand step.

## Solution

Each client gets the state **Trades closed** after its Lock. In that state, each trade tool is closed, and the trade history stays.

- A site build after the Lock has no "Trade Analyzer" menu item, no analyzer row in the Tools chapter of the home page, no analyzer line in the Site answer, no trade Topics in the front door, and no Deadline banner.
- An old link to `/analyze/`, with or without a query, opens a short closed page. It says "The trade deadline has passed. Trades open again next season." and links to Home.
- A trade question at the front door gets the same line from code, with no Claude call.
- The API refuses each trade route after the Lock with the closed reply. It makes no Claude call and no Jev call. The fair warm-up skips the client.
- The weekly trade cards, the Topic `leaders_trades`, and the transaction history of each manager page stay.
- The code stays. A new `lock` for the next season opens the tools again.

`lock` in `client.toml` is the one source of the Lock. CPC keeps its `lock`. NorCal gets `lock = "2026-12-15T00:00:00-05:00"`. A client with no `lock` never has trades closed. A new value, `deadline_week = true`, turns on the Deadline banner and the Trade Wire, so the NorCal `lock` closes the NorCal trades and shows no banner.

## User Stories

1. As a CPC manager, I want the trade tools gone from the site after the deadline, so that I do not plan a trade that Sleeper refuses.
2. As a CPC manager, I want no "Trade Analyzer" item in the menu after the deadline, so that the menu shows only what I can use.
3. As a CPC manager, I want no analyzer row in the Tools chapter of the home page after the deadline, so that the home page does not offer a closed tool.
4. As a CPC manager with an old bookmark to `/analyze/`, I want a closed page that tells me why, so that I do not think the site broke.
5. As a CPC manager with an old prefill link such as `/analyze/?team=3&with=6&give=…`, I want the same closed page, so that each old link gives the same answer.
6. As a CPC manager with an old link to `/analyze/?mode=find`, I want the same closed page, so that the Finder link also explains the close.
7. As a CPC manager on the closed page, I want one link to Home, so that I can go back to the front door in one tap.
8. As a CPC manager at the front door, I want no trade chips and no trade Suggestions, so that the front door offers only Topics that work.
9. As a CPC manager who types a trade question at the front door, I want the line "The trade deadline has passed. Trades open again next season.", so that I know why I get no trade answer.
10. As a CPC manager, I want the answer to a typed trade question to be the closed line and never "I can't answer that.", so that the reason is clear.
11. As a CPC manager who asks the Site answer what the site can do, I want no analyzer line, so that the answer lists only open Tools.
12. As a CPC manager, I want the front door Tour to stop naming a trade as an example question, so that the Tour does not offer a closed Topic.
13. As a CPC manager, I want no Deadline banner and no Trade Wire after the Lock, so that the site shows no event that ended.
14. As a CPC manager, I want the trade cards of each weekly page to stay, so that I can still read the trades of the season.
15. As a CPC manager, I want the Topic "Position leaders and recent trades" to stay, so that the recent trades stay in the front door.
16. As a CPC manager, I want the transaction history of each manager page to stay, so that the league record stays whole.
17. As a CPC manager with a page that loaded before the deploy, I want a press of a trade tool to get the closed reply, so that an old page cannot use a closed tool.
18. As the commissioner, I want the API to refuse each trade route after the Lock, so that a direct call cannot spend money on a closed tool.
19. As the commissioner, I want the fair warm-up to skip a client with trades closed, so that a deploy does not spend about $1.46 of Jev for nothing.
20. As the commissioner, I want the front door Suggestions to make no trade facts for a client with trades closed, so that each Suggestions call spends no Jev on trades.
21. As the commissioner, I want one `lock` value per client as the one source of the close, so that the site and the API always agree.
22. As the commissioner, I want a NorCal `lock` of 2026-12-15 00:00 Eastern now, so that NorCal closes itself after week 14 with no hand step.
23. As a NorCal manager, I want the trade tools to stay open until the NorCal Lock, so that I can trade until the NorCal deadline.
24. As a NorCal manager, I want no Deadline banner and no Trade Wire, so that I see no event that my league did not get.
25. As the commissioner, I want `deadline_week = true` to turn on the Deadline banner and the Trade Wire, so that a `lock` alone does not start a Deadline week.
26. As the commissioner, I want a client with no `lock` to keep its trade tools open, so that a new client works with no Lock.
27. As the commissioner, I want the trade code to stay, so that a new `lock` next season opens the tools again with no rebuild of the features.
28. As the commissioner, I want the site build to decide the close, so that the site needs no second code path in the browser.
29. As the commissioner, I want the weekly build on the Tuesday after a Lock to close the site, so that the close needs no extra deploy.
30. As a CPC manager, I want the closed page to look like the rest of the site, so that it reads as a planned state and not as an error.

## Implementation Decisions

### The values of the client

- `lock` under `[values.analyzer]` stays the one source of the Lock, as now. It holds a time with its UTC offset.
- NorCal gets `lock = "2026-12-15T00:00:00-05:00"`, the end of the Monday night games of week 14.
- A new boolean `deadline_week` under `[values.analyzer]` turns on the Deadline banner and the Trade Wire. It defaults to false. CPC sets it to true. NorCal does not set it.
- **Trades closed** is true for a client when it has a `lock` and the time is at or after the Lock. A client with no `lock` is never closed. Each app computes it with one small pure function of the Lock and the time.

### The site

- The build computes Trades closed once, at build time, from the Lock and the build clock. It passes it on in the generated client values.
- With trades closed, the build:
  - leaves out the analyzer item of the menu, the analyzer home tool row, and the analyzer line of the Site answer.
  - writes the closed page at `/analyze/` in place of the analyzer page. The analyzer page and its code stay in the repo.
  - leaves out the trade Topics `trade_ideas`, `trade_check`, and `sell_high` from the chips, the day order, the More list, and the follow-ups, and leaves out the trade block strip.
  - leaves out the Deadline banner and the Trade Wire.
  - uses a Tour line that names no trade.
- The Deadline banner shows only for a client with `deadline_week = true`, and only before the Lock. The one closed day after the Lock goes away. The banner of an open page still reads the clock of the reader and hides at the Lock by itself.
- The closed page has the top band of the site, one line of copy, and one link to Home. The copy is "The trade deadline has passed. Trades open again next season." It never says "Lock" or "Rosters are locked". The page does not read the query, so each old link of the analyzer gives the same page.
- The page of a build before the Lock keeps each tool. A press there after the Lock gets the closed reply of the API, and the tool shows the closed line.

### The API

- The API parses `lock` from the client values and computes Trades closed at the time of each request.
- With trades closed, these routes answer with the closed reply and make no Claude call and no Jev call: `/analyze`, `/find`, `/trade-check`, `/trade-ideas`, `/find-stream`, `/sell-high`, and `/deadline/trades`.
- The closed reply is HTTP 410 with a JSON body: `{"closed": true, "line": "The trade deadline has passed. Trades open again next season."}`. Each client of the site shows the `line` of the body.
- `/teams` stays open, because it lists the teams and is not a trade tool.
- `/ask`: when Jev routes a question to a trade Topic for a client with trades closed, the answer is the closed line from code, with no Claude call. The free answer gets no trade tool for such a client.
- `/suggestions` makes no `trade_ideas` fact and no `sell_high` fact for a client with trades closed, and offers no trade Topic.
- The fair warm-up skips a client with trades closed. A press or the Trade Wire never wakes it for that client.

### The terms

- `GLOSSARY.md` holds **Trades closed** (commit 081c0736). Deadline week now runs until the Lock, and the Deadline banner hides at the Lock.
- The spec adds `deadline_week` to the glossary entry of Deadline week: the value that turns it on.

## Testing Decisions

A good test checks the behavior that a manager or a caller sees: which route exists, which menu item shows, what a route answers. It never checks a private helper.

The seams, one per app:

1. **The site build.** Build the client with a Lock in the past and with a Lock in the future, then read the built output: the menu, the home tools, the Site answer lines, the front door Topics, the banner, and the page at `/analyze/`. Prior art: `client-steps.test.mjs`, the menu tests under `_routes/*/menu.test.ts`, `shell-props.test.ts`, and `page-site.test.tsx`. One Playwright spec opens `/analyze/` and `/analyze/?mode=find` on a closed build and checks the line and the Home link, at the four viewports of the house rule. Prior art: `deadline-banner.spec.ts`.
2. **The API routes.** Call each trade route with the FastAPI test client for a client whose Lock passed, and for one whose Lock has not passed. Check the 410 body, and check that the fake Jev and the fake Claude got no call. Check `/ask` with a trade question, `/suggestions`, and the fair warm-up. Prior art: `test_trade_topics.py`, `test_trade_wire.py`, `test_fair_warm.py`, `test_suggestions.py`, `test_ask.py`.

The time is a parameter of the pure function, so each test sets the time and never waits for a date.

A flag change in `client.toml` needs the full site and API suites, not only `make check-fast`, because some tests read the real `client.toml` (lesson of PR #85).

## Out of Scope

- The eggs. Brian says the egg code is dead code. The analyzer egg of the CPC egg store stays as it is.
- A delete of the trade code. The code stays, so that the next season's `lock` opens the tools again.
- A browser check of the Lock for the menu and the closed page. The build decides.
- A Lock per season. `lock` stays one value. The commissioner sets the next one each August.
- A NorCal Deadline week. NorCal gets no banner and no Trade Wire.
- A change to the trade history: the weekly trade cards, `leaders_trades`, and the transaction history.
- A rule that computes the Lock from the Sleeper deadline week.

## Further Notes

- The CPC Lock passed at 00:00 Eastern on 2026-11-24. The first deploy of this spec closes the CPC site. The API closes CPC at the deploy of the API.
- The NorCal Lock is 2026-12-15 00:00 Eastern. The weekly build of that Tuesday closes the NorCal site. The API closes NorCal at the exact time.
- The front door names no internal name in copy: no Jev, Advisor, or Finder.
