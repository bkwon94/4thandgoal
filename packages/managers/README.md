# managers: the manager pages of one league

## Knows

- The entries of the managers file, the roster grade, the moves, the best adds, the top performers, and the season so far (`cpc-managers`, imported as `managers`).
- The writer of `managers.json` in `render.py`. The pipeline calls it only when the client takes the managers package.
- A league with no median game has no median in any week of an entry, so the points line has no median line.
- The tunables of the roster grade in `tunables.py`: the weights, the hole cost, the depth spares, and the letter bands.
- The manager page, the managers index, the schema and the types of `managers.json`, and its fixture (`@cpc/managers`).
- Package values: none yet.

## Ports

- `SeasonInputs` of `league`: the saved history, the snapshot, the projections ahead, and the chart. The pipeline loads them and passes them in.
- The odds and the power rank of a manager page come from the rankings file. The site app joins them into each entry, so the site side imports no rankings code.

## Does not do

- It imports no app and no core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
- It reads no raw week and no saved facts file of its own, except `saved_awards` in `season.py`. The pipeline gives the roster slots, the players, and the awards.
- It sends no Claude call.
- It builds no route and reads no file on the site. The loader and the route files stay in the site app, because they read files and join the rankings file.
