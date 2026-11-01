# Six layers, and a module imports only downward

The package had grown one direct import cycle, two indirect ones, and a library module that imported
the orchestrator. We split the modules into six layers: model, provider, load, facts, write, output.
The model layer is lowest because the provider returns the models and so must import them.
A test holds the map. A module imports only from its own layer or a lower one. The test fails on any
upward import. The API package imports model, load, facts, and write, never output. We chose a test,
not a move of files, so the rule applies before any file moves and the map stays explicit.

The test is `tests/test_layers.py`. Its `LAYER_OF` dict is the map.
