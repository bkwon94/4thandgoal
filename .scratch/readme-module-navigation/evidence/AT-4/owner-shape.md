Implementation revision: `dad744db4f3b49732adc1586e08c34be2f381f73`.
Base revision: `17f45a15d1c324e36beefd0da29b77fe56b7ef91`.
All source excerpts below come from Git objects at the stated revision.
No behavior test or cold task runs during this static capture.

Counts use splitlines(); each blank physical line counts. Each file ends with a newline.

| Document | Physical lines | Headings in order | Extra heading |
| --- | --- | --- | --- |
| `apps/site/src/lib/data/README.md` | 23 | # src/lib/data: the loaders of the published files → ## Knows → ## Ports → ## Does not do | none |
| `apps/pipeline/src/cornerstone/README.md` | 24 | # cornerstone → ## Knows → ## Ports → ## Does not do | none |
| `apps/api/src/cornerstone_api/README.md` | 24 | # cornerstone_api → ## Knows → ## Ports → ## Does not do | none |
| `packages/analyzer/README.md` | 24 | # analyzer: the trade analyzer and the trade finder → ## Knows → ## Ports → ## Does not do | none |
| `packages/analyzer/site/form/README.md` | 24 | # packages/analyzer/site/form: the trade analyzer and the trade finder → ## Knows → ## Ports → ## Does not do | none |
| `packages/week/README.md` | 22 | # week: the weekly report of one league → ## Knows → ## Ports → ## Does not do | none |
| `packages/week/python/src/week/sheet/README.md` | 23 | # week.sheet → ## Knows → ## Ports → ## Does not do | none |

D13 receives this explicit check. Existing rules do not traverse nested package Python folders.
Test pointers remain within Knows; no separate test heading exists.

## `apps/site/src/lib/data/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–23

```text
1: # src/lib/data: the loaders of the published files
2: 
3: ## Knows
4: 
5: - [week-data.ts](week-data.ts) owns the archive. `listWeekSummaries` sorts seasons and weeks numerically, newest first. [week-data.test.ts](week-data.test.ts) checks cross-season order and weeks 2 and 10.
6: - One loader per published file: the week page file, the rankings file, the managers file, `waiver.json`, `midseason.json`, and `sim.json`.
7: - Where each file sits under `public/`, and which week folders hold `waiver.json`.
8: - The join of the managers file with the last week of the rankings file.
9: - The teams of the latest week for the sheet of Your team on the front door, in `front-door-data.ts`.
10: - Whether the waiver route and the managers route are on. `next.config.ts` builds each one only when its file exists.
11: - The shared read of a published file in `published-file.ts`: the check of the schema version, then the parse.
12: - The test of every published file against its schema, in `src/lib/data/published-files.test.ts`.
13: 
14: ## Ports
15: 
16: - The reads of `public/` with `node:fs`, at build time only.
17: 
18: ## Does not do
19: 
20: - It owns no shape. The [pipeline](../../../../pipeline/README.md) owns each shape, and each package holds the schema of its own file (ADR 0013).
21: - It runs in no browser. Only the app layer and `next.config.ts` call a loader (ADR 0012).
22: - It writes no file. The pipeline publishes every file under `public/`.
23: - It formats no number. Each package holds its own formats.
```

## `apps/pipeline/src/cornerstone/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–24

```text
1: # cornerstone
2: 
3: ## Knows
4: 
5: - The weekly build: fetch from the provider, parse, build the fact sheet, write, verify, render, and publish. [publish.py](publish.py) owns `run_publish` and limits commits to the client season paths. [test_rule_publish.py](../../tests/test_rule_publish.py) checks stray files and other seasons.
6: - The `advisor-eval` command of the CLI. The `analyzer` package holds the fact sheet, the Advisor, and the Finder.
7: - The build of each week and the season files. The `rankings`, `managers`, and `waiver` packages hold their own rules.
8: - The build and the publish of the midseason report: `midseason` runs the sim through `season_sim.py`, reads the pairs left through `season_schedule.py`, and writes the draft and the review file, and `midseason-publish` checks each blurb again and commits `midseason.json` and `sim.json`.
9: - The six layers: model, provider, load, facts, write, output. A module imports only from its own layer or a lower one.
10: - The shared kernel is the league package in `packages/league/`. Every outside service enters through it.
11: - The fact tokens, the writer, the verifier, and the default voice are the facts package in `packages/facts/`.
12: - `LAYER_OF` in `tests/test_layers.py` gives the layer of each module. `docs/adr/0010-six-layers-import-downward-only.md` gives the reason. The terms are in `GLOSSARY.md`.
13: 
14: ## Ports
15: 
16: - `Writer` in `league/claude_port.py`: the one Claude call. `ClaudeWriter` in `facts/writer.py` implements it. Its key is `ANTHROPIC_API_KEY`.
17: - `Jev` in `league/jev_port.py`: the one TypeSafe Jev request. `TypeSafeJev` in `league/jev.py` implements it. Its key is `TYPESAFE_API_KEY`.
18: - The `Provider` port is in `league/provider/`. `tests/fakes.py` holds the one fake of each port: `FixtureProvider`, `FakeWriter`, and `FakeJev`.
19: 
20: ## Does not do
21: 
22: - It never imports `cornerstone_api`. The [API owner](../../../api/src/cornerstone_api/README.md) serves the trade analyzer over HTTP.
23: - It builds no HTML. The site repo builds the HTML from each published file.
24: - No module reads a global client. The CLI or the API entry builds the Client once with `load_client` and passes it down.
```

## `apps/api/src/cornerstone_api/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–24

```text
1: # cornerstone_api
2: 
3: ## Knows
4: 
5: - The FastAPI app that serves the trade analyzer to the site of each client.
6: - At start it reads each folder under `clients/`. A bad `client.toml` stops the start with the file and the key.
7: - It mounts the analyzer routes of the `analyzer` package at `/clients/<slug>/`. The old paths with no client answer as `cpc`.
8: - It mounts the eggs routes of the `eggs` package at `/clients/<slug>/eggs/` for each client of the package, with one SQLite file per client in `CORNERSTONE_EGGS_DIR`.
9: - The ask route of the front door at `/clients/<slug>/ask`, behind the passphrase. One Jev request routes each typed question, and the route table in `ask.py` reads the answers. `ask_wording.py` holds every word sent to Jev. An honest miss writes one entry in the miss log, one SQLite file per client in `CORNERSTONE_ASK_DIR`, kept 90 days (ADR 0031).
10: - The trade Topics of the front door at `/clients/<slug>/trade-check` and `/clients/<slug>/trade-ideas`, behind the passphrase, in `trade_topics.py`. A typed trade check has one Jev request that picks the player of each side from the real rosters, with its words in `trade_wording.py`. An unsure pick gives the form of the Trade page. Each route streams a plain step for each stage of the Advisor, then the whole Answer, in the event stream of the AI SDK. Trade ideas runs whatever the `finder` flag says. Sell high at `/clients/<slug>/sell-high` streams the same way, with the sell high press of the `analyzer` package.
11: - The free answer of the ask box at `/clients/<slug>/ask/free`, behind the passphrase. The route runs again first, so only a question that Jev routes to a free answer reaches Claude. Claude Sonnet 5.5 runs at `low` effort through Pydantic AI, with the tools of `free_tools.py` over the saved weeks of this season and at most 4 tool calls. The text streams through `VercelAIAdapter` to `useChat` of the site. After the last word, one Jev request checks each sentence against the tool results, with one rewrite and then the honest miss. `free_wording.py` holds every word sent to Claude and to Jev for it. Each typed question carries the earlier turns of its Thread, cut to about 8,000 tokens, as Jev state for the route and as earlier messages for Claude, with a cache mark. The check never reads them. `chat_turns.py` holds them and their words.
12: - The refresh route that a daily cron pings.
13: - The passphrase check of each client, from `CORNERSTONE_PASSPHRASE_<SLUG>`, the commissioner key check of each client of the eggs package, from `CORNERSTONE_COMMISSIONER_KEY_<SLUG>`, the rate limit of each address, the limit of the egg check of each address, the state of each client, and the settings from the environment. [caps.py](caps.py) owns daily answer allowances per team and local calendar day. [test_caps.py](../../tests/test_caps.py) checks team isolation and the next-day reset.
14: - The terms are in `GLOSSARY.md`.
15: 
16: ## Ports
17: 
18: - It takes the `Jev` port of the `league` package for the ask route, the trade picks, and the check of the free answer. `create_app` takes a `jev`, so a test gives `FakeJev`. The free answer runs the model of its Pydantic AI agent, and a test sets `app.state.free_model` to a function model of Pydantic AI.
19: 
20: ## Does not do
21: 
22: - It holds no grade rule and no prompt of the trade analyzer. The [analyzer owner](../../../../packages/analyzer/README.md) holds them, with the grade limit and the caches. The only prompt here is the free answer of `free_wording.py`.
23: - It imports no pipeline code. Only its tests read the fixtures of the pipeline tests.
24: - It imports nothing from the output layer of ADR 0010, so it writes no page.
```

## `packages/analyzer/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–24

```text
1: # analyzer: the trade analyzer and the trade finder
2: 
3: ## Knows
4: 
5: - The proposed trade of `trade.py`, the Measures and `Side` of `measures.py`, and the trade facts (`cpc-analyzer`, imported as `analyzer`). The read of the Advisor in `advisor.py`, with the Jev answers of `trade_jev.py`, and the team facts of `team_facts.py`. The Finder search of `finder_search.py`: the partner filter, the targets, the offers, and the shortlist, with its Jev requests in waves by `jev_waves.py`. The Finder pick of `finder_pick.py`: one sheet per shortlist offer, the Advisor pick of up to 3 trades with a headline and Bullets, and the fallback to the shortlist with fact lines. The sell high pick of `sell_high.py`: the sheet of one roster in `sell_facts.py`, with the trade value, the lineup value, the trend of the last 4 weeks, and the schedule ahead of each player side by side, and the Advisor pick of up to 3 players to sell with the guards and the Jev checks of the read.
6: - The rule prompts `prompts/advisor.md`, `prompts/finder_pick.md`, `prompts/finder_pick_repair.md`, and `prompts/sell_high.md`, and the numbers of `tunables.py`.
7: - The analyzer routes of the API in `routes.py`: the teams, the analyze route, and the find route, with the result cache, the teams cache, and the grade limit. The sell high press of the front door is there too, with no route of its own.
8: - [GradeLimiter in ratelimit.py](python/src/analyzer/ratelimit.py) counts grades per client and address and saves daily counts across restarts. [API integration tests](../../apps/api/tests/test_api.py) check the restart limit and HTTP 429. Each client has its own result cache, so the roster ids of two leagues never share a grade.
9: - The cache key reads the points key of the League settings of the client, such as `pts_ppr` for a full PPR league.
10: - The [form owner](site/form/README.md), the finder, the API client, the passphrase, the teams store, and the team picker of the site (`@cpc/analyzer`). The site calls `/clients/<slug>/...`.
11: - Package values, under `[values.analyzer]`: `finder`, the trade finder on the analyzer page. The default is false.
12: - The model of its package values in `values.py`, and its exported JSON Schema `values.schema.json`. `make schema` rewrites the file.
13: 
14: ## Ports
15: 
16: - `SnapshotSource` in `routes.py`: the live snapshots of one client. The API app gives its `Sources`, and a test gives fixture-backed ones.
17: - `Analyzer` and `FinderPicker` in `routes.py`: the Advisor calls of the grade and of the Finder pick. Each takes an optional `Stage` of `stage.py`, a plain line per stage for the front door. A test gives a stub call. The Advisor takes the Jev port of `league`, and a test gives `FakeJev`. `FinderSearch` in `routes.py` is the Finder search with the real Jev, and a test gives a search with `FakeJev`. `SellHighPicker` in `routes.py` is the sell high pick, and a test gives a stub call.
18: 
19: ## Does not do
20: 
21: - It imports no app and no other core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
22: - It mounts no route. The [API owner](../../apps/api/src/cornerstone_api/README.md) mounts the routes at `/clients/<slug>/` and loads each client. That owner also controls daily answer allowances through `caps.py`.
23: - Of a client folder, it reads the voice folder `prompts/` with the Playbook `playbook.md`, and the playoff odds in `published/<season>/rankings.json`.
24: - It writes no published file.
```

## `packages/analyzer/site/form/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–24

```text
1: # packages/analyzer/site/form: the trade analyzer and the trade finder
2: 
3: ## Knows
4: 
5: - The analyzer page body: the passphrase dialog, the trade form, and the result. [team-picker.tsx](team-picker.tsx) restores selected-team focus after Change my team. [team-picker.test.tsx](team-picker.test.tsx) checks the selected radio.
6: - The trade form, the Stack: the hero, the teams row, a card for each side, the sheets, the grade bar with its Ready halo, the fold line, the sweep, and the error box.
7: - The result of one analyze document: the read hero with the Lean on its 5-step scale, the Case, and the fairness line, the swap card, one tab per side, and the Bullet rows in `bullet-rows.tsx`, which the Finder card reuses.
8: - The trade finder, with an optional partner and up to three picks of the Advisor, each with a headline, the swap, and the Bullet rows. After a fallback, each trade of the shortlist shows its fact lines. The teams prefetch of the home page.
9: - `useRequest`, the guard of a call from a part to the API: the run id, the abort controller, and the unmounted flag.
10: 
11: ## Ports
12: 
13: - The site API, through the client in `../lib/api.ts`. The calls are teams, analyze, and find, at `/clients/<slug>/`.
14: - The passphrase in local storage, through `../lib/passphrase.ts`.
15: - The teams list in session storage, through `../lib/teams-store.ts`.
16: - GoatCounter events, through `packages/design/site/lib/usage.ts`.
17: - Player headshots from the Sleeper CDN. The URL comes in the teams answer of the site API.
18: 
19: ## Does not do
20: 
21: - It grades no trade. The [analyzer Python owner](../../README.md) grades it through the site API, and this folder shows the answer.
22: - It shows no roster grade. The roster grade lives in the managers part of the site.
23: - It defines no API shape. `../lib/schemas/api.ts` holds the response schemas.
24: - It reads no file, no env, and no config, and it imports no app. The page gives the API target and the finder flag.
```

## `packages/week/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–22

```text
1: # week: the weekly report of one league
2: 
3: ## Knows
4: 
5: - The [sheet owner](python/src/week/sheet/README.md) holds roster projections. The sheet chapters except rankings, the league and matchup facts, and the page writer of `page.json` (`cpc-week`, imported as `week`).
6: - The week chapters, the schema and the types of `page.json`, and `who` (`@cpc/week`). The loader of `page.json` stays in the site app, because it reads files.
7: - The median text in `prompts/median.md`. The writer and the verifier get it only when the league scores a median game.
8: - A league with no median game has no MED facts, no median part in the impact fact, and no Median Game chapter.
9: - The tunables of the week in `tunables.py`: the shootout cut, the storyline weights, the key starter rule, and the award cap.
10: - Package values: it has no values.
11: 
12: ## Ports
13: 
14: - The chapter port `ChapterSource` in `sheet/port.py`: a chapter of another package, with its facts and the odds it computes. The app passes the source of each package that the client takes, so a client with no rankings has no rankings chapter and no odds.
15: - The registry of the site build lists the home chapter of each package that the client takes, and no other. Each one sits in `apps/site/src/app/_routes/<package>/home.tsx`.
16: 
17: ## Does not do
18: 
19: - It imports no app and no core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
20: - It holds no odds engine and no power rankings. The [rankings owner](../rankings/README.md) gives them through the chapter port. Roster projections belong to the sheet, not that odds engine.
21: - It writes no rankings, managers, or waiver file. Each package writes its own.
22: - It sends no Claude call of its own. The writer and the verifier of `facts` write and check each blurb.
```

## `packages/week/python/src/week/sheet/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–23

```text
1: # week.sheet
2: 
3: ## Knows
4: 
5: - It builds the facts of each fact group into the fact sheet of one week, and puts the facts into each chapter.
6: - It builds the bundle that each chapter reads, and it writes and reads the bundle file.
7: - The entry: outside this folder, a module imports only `week.sheet` or `week.sheet.base`.
8: - A league with no median game gets no MED facts, no median part in the impact fact, and no Median Game chapter.
9: - [base.py](base.py) owns `projected_totals`, which reads current roster players, including additions after the scored week. [test_sheet.py](../../../../../../apps/pipeline/tests/test_sheet.py) checks additions and drops after lineup lock.
10: - The terms are in `GLOSSARY.md`.
11: 
12: ## Ports
13: 
14: - `sheet/port.py` is the chapter port. A source of another package gives its facts, its chapter, and the odds.
15: - `sheet/assemble.py` calls `provider.sleeper.fetch_news` by default, so the sheet reaches the Sleeper news feed.
16: 
17: ## Does not do
18: 
19: - It writes no prose and makes no Claude call. `facts/writer.py` writes each blurb.
20: - It checks no blurb. `facts/verifier.py` does.
21: - It holds no odds engine and no rankings chapter. The [rankings owner](../../../../../rankings/README.md) gives both through the chapter port.
22: - It writes no page. `week/page.py` writes `page.json`.
23: - It builds no fact sheet of a proposed trade. `cornerstone/trade_facts.py` does.
```

