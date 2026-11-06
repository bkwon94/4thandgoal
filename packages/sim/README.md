# sim: the season sim of the rest of the regular season and the playoff bracket

## Knows

- The package values in `values.py` (`cpc-sim`, imported as `sim`). It has no values.
- The sim in `season.py`: the draw of the weekly odds over the rest of the regular season, then the bracket of the playoff weeks. The bracket reseeds after each round when `reseed` of the League settings is on. It counts the playoff, the bye, the final, the title, each seed, and each final win total over 10,000 runs, and keeps the first 200 runs.
- The numbers of the draw in `tunables.py`.
- The shape of `sim.json` and its writer in `published.py`.
- The site part, the replay, comes with ticket 13. It reads `sim.json` and nothing of the report.

## Ports

- It declares no port. `season_sim` takes the scores, the records, the pairs left, and the projected totals as data. An app loads them, runs the sim, and hands the result to the report through the port of `midseason`.

## Does not do

- It imports no app and no other core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
- It knows nothing of the midseason report, so a weekly page or a standalone page can use it later.
- It does not import `rankings`. A parity test holds its draw to the weekly playoff odds.
