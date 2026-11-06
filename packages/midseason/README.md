# midseason: the midseason report, one edited moment per season

## Knows

- The state of the league in `state.py`: the full record, points for and against, the streak, and the playoff odds of each team.
- The draft steals and busts in `draft.py`: the cost rank at the position against the points rank, the top 5 of each, the "hurt" or "just bad" tag of a bust, and "the one that got away" line of a steal. `draft_injuries.py` counts the games each player missed with an injury.
- The shape of `midseason.json` and its writer in `published.py`, with the acts and the chapters (`cpc-midseason`, imported as `midseason`).
- The prose in `prose.py`: the facts and the prose blocks of each chapter, a roast block per chapter unless the roast is off, and the roast terms of `prompts/roast.md`.
- The review file in `review.py`: each blurb with its prose block, the facts it cites, and the verifier result.
- The package values in `values.py`: `roast`, one of `off`, `warm`, and `hot`. The default is `hot`.
- A client that takes `midseason` takes `sim` too. The client check of `league` fails a client with `midseason` and no `sim`.

## Ports

- `playoff_odds` of `league_state` in `state.py` takes the playoff odds by roster ID from the app. The report imports no odds engine.
- `draft_value` in `draft.py` takes the picks of the draft from the app, and `injured_games` takes the weekly injury report by player ID. The package fetches nothing.
- `write_prose` and `recheck_prose` take the Claude call from the app. Each blurb goes through the writer and the verifier of `facts`, so the package has no writer of its own.

## Does not do

- It imports no app and no other core package, only `league` and `facts`. It never imports `sim`. `tests/test_layers.py` of the pipeline checks it.
- It writes nothing to `published/`. The build writes `midseason.json`, `midseason-facts.json`, and `midseason-review.md` into the build folder of the season only. The publish of the app copies `midseason.json` and `sim.json`.
- It adds no menu item.
