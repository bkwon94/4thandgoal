# cornerstone

## Knows

- The weekly build: fetch from the provider, parse, build the fact sheet, write, verify, render, and publish.
- The trade analyzer: the rubric, the adjusters, the grade, and the finder.
- The waiver board, the power rankings, the playoff odds, and the managers file.
- The six layers: model, provider, load, facts, write, output. A module imports only from its own layer or a lower one.
- The shared kernel is the league package in `packages/league/`. Every outside service enters through it.
- `LAYER_OF` in `tests/test_layers.py` gives the layer of each module. `docs/adr/0010-six-layers-import-downward-only.md` gives the reason.
- The prompts in `prompts/`. That folder has no `__init__.py`, so it is not a package.
- The terms are in `GLOSSARY.md`.

## Ports

- `Writer` in `league/claude_port.py`: the one Claude call. `ClaudeWriter` in `writer.py` implements it.
- The `Provider` port is in `league/provider/`. `tests/fakes.py` holds the one fake of each port.

## Does not do

- It never imports `cornerstone_api`. That package serves the trade analyzer over HTTP.
- It builds no HTML. The site repo builds the HTML from each published file.
- No module reads a global client. The CLI or the API entry builds the Client once with `load_client` and passes it down.
