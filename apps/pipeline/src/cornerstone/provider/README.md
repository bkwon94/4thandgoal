# cornerstone.provider

## Knows

- The fetches of the league data from the provider, and the raw shape of each file at the HTTP call.
- The Sleeper adapter, with one raw JSON file per endpoint and a disk cache for the large players file.
- The map of the Sleeper league file into the League settings, with the league file of each season as its cache.
- Each Sleeper fetch takes an optional `httpx` transport, so a test passes an `httpx.MockTransport`.
- The terms are in `GLOSSARY.md`.

## Ports

- `Provider` in `provider/base.py`: the six fetches that each provider gives, with `fetch_settings` for the League settings. `provider/sleeper.py` implements it.

## Does not do

- It holds no league rule. It fetches the raw files, saves them, and reads them back.
- It does not turn the raw data into the domain models, except the League settings. `cornerstone/parse.py` does.
- It derives no size from the League settings. `cornerstone/league_settings.py` does.
- It picks no history week. `cornerstone/history.py` picks the folder and the weeks, and `sleeper.py` writes the files.
- It fetches no nflverse file and reads no trade value chart. `cornerstone/nflverse.py` and `cornerstone/chart.py` do.
