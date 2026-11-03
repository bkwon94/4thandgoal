# Ruff baseline

Branch `ruff-baseline`, base main `9f25630`. Worktree `cornerstone-fantasy-sleeper-weekly-report.ruff`.

## Commits

1. `b7ac86d` Set ruff line length in pyproject. `[tool.ruff] line-length = 120`. The `lint` target runs `uv run ruff check src tests`. The bare command reported 135.
2. `97077a9` Fix E731, F401, F841 findings. Six lambdas became short `def` functions. Two imports left. The unused `margins` dict in `facts_league.py` is gone. The autofix left a bare expression, and the line was deleted by hand.
3. `e77f834` Rename l variables to plain words (65 cases).
4. `ca8bd7b` Wrap lines over 120 characters (61 cases from the original count, plus 2 lines that the renames made long).

## Rename words

- `line` (a `PlayerLine`): `cli.py`, `facts_league.py`, `facts_matchup.py`, `sheet.py`, `conftest.py`, `test_facts_matchup.py`, `test_parse.py`, `test_facts_nflverse.py`, `test_trades.py`, `test_render.py`. These files already use `line` for the same thing.
- `leader` (a `PositionLeader`): `sheet.py` line 1576, `test_sheet.py`, `test_render.py` line 198.
- `loser` (the loser team name, from `w, l = ...`): `sheet.py` lines 474 to 476 and 564 to 569. The `w` variable stays.
- `letter` (a rubric letter): `test_api.py`.

Left: none.

## Notes

- Wrapped docstrings and comments split at a word. The text is the same.
- An AST compare of every changed file against HEAD matched. Docstring whitespace was normalized in that compare.

## Final ruff output

`uv run ruff check src tests` prints no findings and exits 0.

## Tests

`uv run pytest -q`: 1081 passed, 9 deselected in 152.18s.
