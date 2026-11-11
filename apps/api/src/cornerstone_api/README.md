# cornerstone_api

## Knows

- The FastAPI app that serves the trade analyzer to the site of each client.
- At start it reads each folder under `clients/`. A bad `client.toml` stops the start with the file and the key.
- It mounts the analyzer routes of the `analyzer` package at `/clients/<slug>/`. The old paths with no client answer as `cpc`.
- It mounts the eggs routes of the `eggs` package at `/clients/<slug>/eggs/` for each client of the package, with one SQLite file per client in `CORNERSTONE_EGGS_DIR`.
- The ask route of the front door at `/clients/<slug>/ask`, behind the passphrase. One Jev request routes each typed question, and the route table in `ask.py` reads the answers. `ask_wording.py` holds every word sent to Jev. An honest miss writes one entry in the miss log, one SQLite file per client in `CORNERSTONE_ASK_DIR`, kept 90 days (ADR 0031).
- The trade Topics of the front door at `/clients/<slug>/trade-check` and `/clients/<slug>/trade-ideas`, behind the passphrase, in `trade_topics.py`. A typed trade check has one Jev request that picks the player of each side from the real rosters, with its words in `trade_wording.py`. An unsure pick gives the form of the Trade page. Each route streams a plain step for each stage of the Advisor, then the whole Answer, in the event stream of the AI SDK. Trade ideas runs whatever the `finder` flag says. Sell high at `/clients/<slug>/sell-high` streams the same way, with the sell high press of the `analyzer` package.
- The free answer of the ask box at `/clients/<slug>/ask/free`, behind the passphrase. The route runs again first, so only a question that Jev routes to a free answer reaches Claude. Claude Sonnet 5.5 runs at `low` effort through Pydantic AI, with the tools of `free_tools.py` over the saved weeks of this season and at most 4 tool calls. The text streams through `VercelAIAdapter` to `useChat` of the site. After the last word, one Jev request checks each sentence against the tool results, with one rewrite and then the honest miss. `free_wording.py` holds every word sent to Claude and to Jev for it. Each typed question carries the earlier turns of its Thread, cut to about 8,000 tokens, as Jev state for the route and as earlier messages for Claude, with a cache mark. The check never reads them. `chat_turns.py` holds them and their words.
- The refresh route that a daily cron pings.
- The passphrase check of each client, from `CORNERSTONE_PASSPHRASE_<SLUG>`, the commissioner key check of each client of the eggs package, from `CORNERSTONE_COMMISSIONER_KEY_<SLUG>`, the rate limit of each address, the limit of the egg check of each address, the state of each client, and the settings from the environment.
- The terms are in `GLOSSARY.md`.

## Ports

- It takes the `Jev` port of the `league` package for the ask route, the trade picks, and the check of the free answer. `create_app` takes a `jev`, so a test gives `FakeJev`. The free answer runs the model of its Pydantic AI agent, and a test sets `app.state.free_model` to a function model of Pydantic AI.

## Does not do

- It holds no grade rule and no prompt of the trade analyzer. The `analyzer` package holds them, with the grade limit and the caches. The only prompt here is the free answer of `free_wording.py`.
- It imports no pipeline code. Only its tests read the fixtures of the pipeline tests.
- It imports nothing from the output layer of ADR 0010, so it writes no page.
