# Six layers, and a module imports only downward

The package had grown one direct import cycle, two indirect ones, and a library module that imported
the orchestrator. We split the modules into six layers: model, provider, load, facts, write, output.
The model layer is lowest because the provider returns the models and so must import them.
A test holds the map. A module imports only from its own layer or a lower one. The test fails on any
upward import. The API package may import every layer below output. We chose a test,
not a move of files, so the rule applies before any file moves and the map stays explicit.

The test is `tests/test_layers.py`. Its `LAYER_OF` dict is the map.

## The sheet entry point

Outside the sheet package, a module imports only `cornerstone.sheet` or `cornerstone.sheet.base`. A
caller then reads one entry, and a chapter module can change with no edit outside the sheet. The rule
reads every import in the file: at load, under `TYPE_CHECKING`, and inside a function. It does not read
`tests/`, so a chapter test may import its chapter module.

The test is `test_no_module_outside_the_sheet_imports_a_chapter_module` in `tests/test_layers.py`.
