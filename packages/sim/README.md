# sim: the season sim of the rest of the regular season and the playoff bracket

## Knows

- The package values in `values.py` (`cpc-sim`, imported as `sim`). It has no values.
- The draw of the rest of the regular season, the playoff bracket, and the writer of `sim.json` come with ticket 03 of `.scratch/midseason-report/`.
- The site part, the replay, comes with ticket 13. It reads `sim.json` and nothing of the report.

## Ports

- It declares no port. An app runs the sim and hands the result to the report through the port of `midseason`.

## Does not do

- It imports no app and no other core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
- It knows nothing of the midseason report, so a weekly page or a standalone page can use it later.
- It does not import `rankings`. A parity test holds its draw to the weekly playoff odds.
