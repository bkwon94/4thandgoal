# cornerstone

## Knows

- The weekly build: the provider fetch, the parse, the fact sheet, the writer, the verifier, the render, and the publish.
- The trade analyzer: the rubric, the adjusters, the grade, and the finder.
- The waiver board, the power rankings, the playoff odds, and the managers file.
- The six layers: model, provider, load, facts, write, output. A module imports only from its own layer or a lower one.
- `LAYER_OF` in `tests/test_layers.py` gives the layer of each module. `docs/adr/0007-six-layers-import-downward-only.md` gives the reason.
- The prompts in `prompts/`. That folder has no `__init__.py`, so it is not a package.
- The terms are in `GLOSSARY.md`.

## Ports

None. The `Provider` port is in `provider/`.

## Does not do

- It never imports `cornerstone_api`. That package serves the trade analyzer over HTTP.
- It renders no HTML. The site repo renders each published file.
- No module reads a global league config. The CLI or the API entry builds it once and passes it down.
