# cornerstone.provider

## Knows

- The fetches of the league data from the provider, and the raw shape of each file at the HTTP call.
- The Sleeper adapter, with one raw JSON file per endpoint and a disk cache for the large players file.
- The terms are in `GLOSSARY.md`.

## Ports

- `Provider` in `provider/base.py`: the five fetches that each provider gives. `provider/sleeper.py` implements it.

## Does not do

- It holds no league rule. It fetches and saves the raw files, and nothing more.
- It does not turn the raw data into the domain models. `cornerstone/parse.py` does.
- It keeps no history of past weeks. `cornerstone/history.py` saves them.
- It fetches no nflverse file and reads no trade value chart. `cornerstone/nflverse.py` and `cornerstone/chart.py` do.
- The provider layer of ADR 0007 holds more than this folder. `tests/test_layers.py` lists each module of the layer.
