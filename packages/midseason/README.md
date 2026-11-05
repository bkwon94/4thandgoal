# midseason: the midseason report, one edited moment per season

## Knows

- The state of the league in `state.py`: the full record, points for and against, the streak, and the playoff odds of each team.
- The shape of `midseason.json` and its writer in `published.py`, with the acts and the chapters (`cpc-midseason`, imported as `midseason`).
- The package values in `values.py`. It has no values yet.
- A client that takes `midseason` takes `sim` too. The client check of `league` fails a client with `midseason` and no `sim`.

## Ports

- `playoff_odds` of `league_state` in `state.py` takes the playoff odds by roster ID from the app. The report imports no odds engine.

## Does not do

- It imports no app and no other core package, only `league` and `facts`. It never imports `sim`. `tests/test_layers.py` of the pipeline checks it.
- It writes nothing to `published/`. The build writes `midseason.json` into the build folder of the season only.
- It adds no menu item.
