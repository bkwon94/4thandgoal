# cornerstone_api

## Knows

- The FastAPI app that serves the trade analyzer to the site of each client.
- At start it reads each folder under `clients/`. A bad `client.toml` stops the start with the file and the key.
- It mounts the analyzer routes of the `analyzer` package at `/clients/<slug>/`. The old paths with no client answer as `cpc`.
- It mounts the eggs routes of the `eggs` package at `/clients/<slug>/eggs/` for each client of the package, with one SQLite file per client in `CORNERSTONE_EGGS_DIR`.
- The ask route of the front door at `/clients/<slug>/ask`, behind the passphrase. One Jev request routes each typed question, and the route table in `ask.py` reads the answers. `ask_wording.py` holds every word sent to Jev. An honest miss writes one entry in the miss log, one SQLite file per client in `CORNERSTONE_ASK_DIR`, kept 90 days (ADR 0031).
- The refresh route that a daily cron pings.
- The passphrase check of each client, from `CORNERSTONE_PASSPHRASE_<SLUG>`, the commissioner key check of each client of the eggs package, from `CORNERSTONE_COMMISSIONER_KEY_<SLUG>`, the rate limit of each address, the limit of the egg check of each address, the state of each client, and the settings from the environment.
- The terms are in `GLOSSARY.md`.

## Ports

- It takes the `Jev` port of the `league` package for the ask route. `create_app` takes a `jev`, so a test gives `FakeJev`.

## Does not do

- It holds no grade rule, no prompt, and no Claude check. The `analyzer` package holds them, with the grade limit and the caches.
- It imports no pipeline code. Only its tests read the fixtures of the pipeline tests.
- It imports nothing from the output layer of ADR 0010, so it writes no page.
