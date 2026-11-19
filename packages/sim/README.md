# sim: the season sim of the rest of the regular season and the playoff bracket

## Knows

- The package values in `values.py` (`cpc-sim`, imported as `sim`). It has no values.
- The sim in `season.py`, the one odds engine (ADR 0037): the draw over the rest of the regular season, then the bracket of the playoff weeks. The bracket reseeds after each round when `reseed` of the League settings is on. It counts the playoff, the bye, the final, the title, each seed, and each final win total over 10,000 runs, and keeps the first 200 runs. It gives the seed, the status, and the swing of each game next week, and `weekly_odds` turns them into the weekly odds.
- The page block of one team in `page.py`: the ladder, the results of each week left, the odds after a loss, and the root-for rows, each by a split of the runs of one sim. A What-if counts its set wins apart, so the sentence names only the wins still open. It also gives the league fact of the Sim tile.
- The rule of the shown odds in `percent.py`, which the team odds, the swings, and the page block share.
- The numbers of the draw in `tunables.py`.
- The shapes of the season `sim.json` and of the week `week-NN/sim.json`, and their writers, in `published.py`.
- The site part in `site/`: the replay of one stored run beside the odds of all runs, and the sim page of Your team. The replay reads `sim.json` and nothing of the report. The page reads the page block of `week-NN/sim.json`, and a tap on a result calls the What-if route through `site/lib/`. The replay of the page in `site/stage/` plays one stored run of the file or of the last What-if answer, picked by its weight.

## Ports

- It declares no port. `season_sim` takes the scores, the records, the pairs left, and the projected totals as data. An app loads them and runs the sim. `rerun` runs the sim of a week file again on the numbers of its draw, so the What-if of the API needs no league data. A `stop` check between blocks of runs lets an app stop the sim. It hands the weekly odds to the week through the chapter port, and the result to the report through the port of `midseason`.

## Does not do

- It imports no app and no other core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
- It knows nothing of the midseason report, so a weekly page or a standalone page can use it later.
- It does not import `rankings`.
