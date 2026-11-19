# The season sim is the one odds engine

The weekly build had two Monte Carlo engines of one model: `rankings/odds.py` for the weekly playoff odds and the swings, and `packages/sim` for the midseason report. A parity test held them together, but sample noise still let two pages show two numbers for one team. The season sim page puts the sim odds in front of each manager each week, next to the rankings odds. We decided that the season sim is the one odds engine. It gives the playoff odds, the bye odds, the seeds, and the swing of each game next week, and `rankings/odds.py` goes away. Brian chose it on 2026-11-18 (spec `season-sim`, decision 02).

## Considered Options

- Keep both engines and the parity test. Each page can still differ by a point from sample noise.
- Keep `odds.py` for the swings and the facts, and take only the playoff and bye odds from the sim. The swing and the odds of one team still come from two draws.
- One engine, the sim. A swing is a What-if with one pick, so the sim gives it from a split of its own runs.

## Consequences

- The sim runs 10,000 runs in each weekly build, not 5,000. The build pays about 1 s more.
- The odds of past weeks in `rankings.json` came from the old engine, and they stay as they are.
- A change to the model of the draw changes one file, not two, and needs no parity test.
