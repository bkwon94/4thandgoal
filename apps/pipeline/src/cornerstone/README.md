# cornerstone

## Knows

- The weekly build: fetch from the provider, parse, build the fact sheet, write, verify, render, and publish.
- The `analyze` and `find` commands of the CLI. The `analyzer` package holds the rubric, the grade, and the finder.
- The waiver board, the power rankings, the playoff odds, and the managers file.
- The six layers: model, provider, load, facts, write, output. A module imports only from its own layer or a lower one.
- The shared kernel is the league package in `packages/league/`. Every outside service enters through it.
- The fact tokens, the writer, the verifier, and the default voice are the facts package in `packages/facts/`.
- `LAYER_OF` in `tests/test_layers.py` gives the layer of each module. `docs/adr/0010-six-layers-import-downward-only.md` gives the reason.
- The rule prompt of the waiver board in `prompts/`, as `RULE_PROMPTS`. The folder is not a package.
- The terms are in `GLOSSARY.md`.

## Ports

- `Writer` in `league/claude_port.py`: the one Claude call. `ClaudeWriter` in `facts/writer.py` implements it.
- The `Provider` port is in `league/provider/`. `tests/fakes.py` holds the one fake of each port.

## Does not do

- It never imports `cornerstone_api`. That package serves the trade analyzer over HTTP.
- It builds no HTML. The site repo builds the HTML from each published file.
- No module reads a global client. The CLI or the API entry builds the Client once with `load_client` and passes it down.
