# midseason: the midseason report, one edited moment per season

## Knows

- The state of the league in `state.py`: the full record, points for and against, the streak, and the playoff odds of each team.
- The injury toll in `injury.py`, Position top 10 in `top10.py`, and the players to watch in `watch.py`, each with its prose block.
- The shape of `midseason.json` and its writer in `published.py`, with the acts and the chapters (`cpc-midseason`, imported as `midseason`).
- The prose in `prose.py`: the facts and the prose blocks of each chapter, a roast block per chapter unless the roast is off, and the roast terms of `prompts/roast.md`.
- The review file in `review.py`: each blurb with its prose block, the facts it cites, and the verifier result.
- The package values in `values.py`: `roast`, one of `off`, `warm`, and `hot`. The default is `hot`.
- A client that takes `midseason` takes `sim` too. The client check of `league` fails a client with `midseason` and no `sim`.

## Ports

- `playoff_odds` of `league_state` in `state.py` takes the playoff odds by roster ID from the app. The report imports no odds engine.
- `injury_toll`, `position_top10`, and `players_to_watch` take the injury report, the Sleeper statuses, the NFL schedule, the expected points, the projections, and the rosters now from the app as plain data.
- `write_prose` and `recheck_prose` take the Claude call from the app. Each blurb goes through the writer and the verifier of `facts`, so the package has no writer of its own.

## Does not do

- It imports no app and no other core package, only `league` and `facts`. It never imports `sim`. `tests/test_layers.py` of the pipeline checks it.
- It writes nothing to `published/`. The build writes `midseason.json`, `midseason-facts.json`, and `midseason-review.md` into the build folder of the season only. The publish of the app copies `midseason.json` and `sim.json`.
- It adds no menu item.
