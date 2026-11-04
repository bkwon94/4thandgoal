# league.provider

## Knows

- The fetches of the league data from the provider, and the raw shape of each file at the HTTP call.
- The Sleeper adapter, with one raw JSON file per endpoint. It takes its cache dir, which holds the large players file, in its constructor.
- The map of the Sleeper league file into the League settings, with the league file of each season as its cache.
- Each Sleeper fetch takes an optional `httpx` transport, so a test passes an `httpx.MockTransport`.
- The projections ahead hold the projection at the points key of the League settings.
- The terms are in `GLOSSARY.md`.

## Ports

- `Provider` in `provider/base.py`: the six fetches that each provider gives, with `fetch_settings` for the League settings. `provider/sleeper.py` implements it.

## Does not do

- It holds no league rule. It fetches the raw files, saves them, and reads them back.
- It does not turn the raw data into the domain models, except the League settings. `league/parse.py` does.
- It derives no size from the League settings. `league/league_settings.py` does.
- It picks no history week. `league/history.py` picks the folder and the weeks, and `sleeper.py` writes the files.
- It fetches no nflverse file and reads no trade value chart. `league/nflverse.py` and `league/chart.py` do.
