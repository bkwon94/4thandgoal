# analyzer: the trade analyzer and the trade finder

## Knows

- The rubric, the adjusters and `Side`, the trade facts, the analysis, the finder, and the finder reasons (`cpc-analyzer`, imported as `analyzer`). The read of the Advisor in `advisor.py`, with the Jev answers of `trade_jev.py`, the team facts of `team_facts.py`, and the Measures of `measures.py`. The Finder search of `finder_search.py`: the partner filter, the targets, the offers, and the shortlist, with its Jev requests in waves by `jev_waves.py`. The Finder pick of `finder_pick.py`: one sheet per shortlist offer, the Advisor pick of up to 3 trades with a headline and Bullets, and the fallback to the shortlist with fact lines.
- The rule prompts `prompts/advisor.md`, `prompts/analysis.md`, `prompts/finder.md`, `prompts/finder_pick.md`, and `prompts/rubric.md`, and the numbers of `tunables.py`.
- The analyzer routes of the API in `routes.py`: the teams, the analyze route, and the find route, with the result cache, the teams cache, and the grade limit.
- The grade limit counts per client and per address. Each client has its own result cache, so the roster ids of two leagues never share a grade.
- The cache key reads the points key of the League settings of the client, such as `pts_ppr` for a full PPR league.
- The trade form, the finder, the API client, the passphrase, the teams store, and the team picker of the site (`@cpc/analyzer`). The site calls `/clients/<slug>/...`.
- Package values, under `[values.analyzer]`: `finder`, the trade finder on the analyzer page. The default is false.
- The model of its package values in `values.py`, and its exported JSON Schema `values.schema.json`. `make schema` rewrites the file.

## Ports

- `SnapshotSource` in `routes.py`: the live snapshots of one client. The API app gives its `Sources`, and a test gives fixture-backed ones.
- `Analyzer` and `FinderPicker` in `routes.py`: the Advisor calls of the grade and of the Finder pick. A test gives a stub call. The Advisor takes the Jev port of `league`, and a test gives `FakeJev`. `FinderSearch` in `routes.py` is the Finder search with the real Jev, and a test gives a search with `FakeJev`.

## Does not do

- It imports no app and no other core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
- It mounts no route. The API app mounts the routes at `/clients/<slug>/` and loads each client.
- Of a client folder, it reads the voice folder `prompts/` with the Playbook `playbook.md`, and the playoff odds in `published/<season>/rankings.json`.
- It writes no published file.
