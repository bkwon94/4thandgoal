# analyzer: the trade analyzer and the trade finder

## Knows

- The rubric, the adjusters and `Side`, the trade facts, the analysis, the finder, and the finder reasons (`cpc-analyzer`, imported as `analyzer`).
- The rule prompts `prompts/analysis.md`, `prompts/finder.md`, and `prompts/rubric.md`, and the numbers of `tunables.py`.
- The analyzer routes of the API in `routes.py`: the teams, the analyze route, and the find route, with the result cache, the teams cache, and the grade limit.
- The grade limit counts per client and per address. Each client has its own result cache, so the roster ids of two leagues never share a grade.
- The cache key reads the points key of the League settings of the client, such as `pts_ppr` for a full PPR league.
- The trade form, the finder, the API client, the passphrase, the teams store, and the team picker of the site (`@cpc/analyzer`). The site calls `/clients/<slug>/...`.
- Package values, under `[values.analyzer]`: `finder`, the trade finder on the analyzer page. The default is false.
- The model of its package values in `values.py`, and its exported JSON Schema `values.schema.json`. `make schema` rewrites the file.

## Ports

- `SnapshotSource` in `routes.py`: the live snapshots of one client. The API app gives its `Sources`, and a test gives fixture-backed ones.
- `Analyzer` and `ReasonWriter` in `routes.py`: the Claude calls of the grade and the finder. A test gives a fake call.

## Does not do

- It imports no app and no other core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
- It mounts no route and reads no client folder. The API app mounts the routes at `/clients/<slug>/` and loads each client.
- It writes no published file.
