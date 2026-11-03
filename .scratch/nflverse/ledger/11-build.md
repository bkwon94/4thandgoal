# Ticket 11 build: the highest-value fallback reads the lineup value

Status: DONE. Branch `nflverse-11`, commit `ba200a5`. Not pushed, not merged.

## What changed

- `src/cornerstone/rubric.py`: `_highest_value_player` falls back to `lineup_value` in place of
  `recent_points_per_game`. It reuses the ticket 10 function from `cornerstone.adjusters`. No second function.
- The import in `rubric.py` swaps `recent_points_per_game` for `lineup_value`. Nothing else in `rubric.py` used the old name.
- The docstring now says the lineup value picks the player, and what the lineup value is. The old text stays otherwise.
- `.scratch/nflverse/issues/11-...md`: the three checklist boxes are ticked. The Status line stays `open`.

## Tests added (`tests/test_rubric.py`, at the end)

1. `test_with_no_chart_a_player_due_back_is_the_highest_value_player_by_his_projection`:
   Diggs (roster 3, 10.17 a game) for Jacobs (due back week 7, projection 18 a game), no chart. Jacobs is the pick.
   It failed before the fix (red), and passes after.
2. `test_with_a_chart_that_lists_every_player_trade_value_picks_the_highest_value_player`:
   the same trade with a chart of Diggs 20 and Jacobs 5. Diggs is the pick, so the chart path does not change.

Both tests call `rubric._highest_value_player` direct. The roster fit gain step comes before the
highest-value step, so a test through `grade` cannot see the pick for this trade.

## Checks

- `uv run pytest -q`: `1038 passed, 9 deselected in 185.26s (0:03:05)`. Main had 1036; the 2 extra are the new tests.
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` before and after. The change adds none.

## Real-data check

`data/2026/week-06/raw/` with no chart: Josh Jacobs is the only player due back (week 7, recent 0,
lineup value 12.21). A trade of Stefon Diggs (10.17) for Jacobs now names Jacobs as the highest-value player.
Before the fix, Diggs was the pick.

## Concerns

- None for the ticket. Note: the fallback also runs when a chart exists but one traded player is unlisted.
  There too, a player due back now counts for his projection. This matches the ticket text.

## Fix round 1

Commit `e974438`. Not pushed, not merged.

1. Handcuff at zero. The fallback branch in `_highest_value_player` now sets each handcuff to `Decimal(0)`, the same
   rule as the chart path. A comment says why.
   Test: `test_with_no_chart_a_handcuff_due_back_is_never_the_highest_value_player`. Mitchell is a handcuff on
   roster 12, due back in week 7 with a projection of 30. Pollard (8.95) is the pick. Without the fix the test fails.
2. Test through `grade`. Test: `test_with_no_chart_a_seller_that_gets_a_player_due_back_gets_the_highest_value_player`.
   Roster 4 (last, a seller) gives Jameson Williams (10.53) for Jacobs (projection 18), no chart. The standing
   reason is "The team is out of the playoff race, and it gets the highest-value player in the trade."

Checks:
- `uv run pytest -q tests/test_rubric.py`: `130 passed in 6.47s`.
- `uv run pytest -q`: `1040 passed, 9 deselected in 159.36s (0:02:39)`.
- `uv run ruff check --line-length 120 src tests`: `Found 135 errors.` No new errors.
