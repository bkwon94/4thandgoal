# cornerstone_api

## Knows

- The FastAPI app that serves the trade analyzer to the site of each client.
- At start it reads each folder under `clients/`. A bad `client.toml` stops the start with the file and the key.
- It mounts the analyzer routes of the `analyzer` package at `/clients/<slug>/`. The old paths with no client answer as `cpc`.
- The refresh route that a daily cron pings.
- The passphrase check of each client, from `CORNERSTONE_PASSPHRASE_<SLUG>`, the rate limit of each address, the state of each client, and the settings from the environment.
- The terms are in `GLOSSARY.md`.

## Ports

None.

## Does not do

- It holds no grade rule, no prompt, and no Claude check. The `analyzer` package holds them, with the grade limit and the caches.
- It imports no pipeline code. Only its tests read the fixtures of the pipeline tests.
- It imports nothing from the output layer of ADR 0010, so it writes no page.
