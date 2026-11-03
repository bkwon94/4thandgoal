# Ticket 11 spec review

Diff: `e29e2b4..ba200a5` on branch `nflverse-11`. Verdict: no Critical, no Important, one Minor. The ticket is met.

## Critical

None.

## Important

None.

## Minor

1. `src/cornerstone/rubric.py:212` — the fallback does not count a handcuff at zero. The comment at
   `rubric.py:228` says the highest-value player counts every handcuff at zero. That holds only on the trade value path.
   This gap existed before the change. The change widens it: a handcuff due back with a projection can now be the pick.
   Fix: in the fallback, set `worth[pid] = Decimal(0)` for each `pid` in `handcuffs`, and add a test.

## Checklist

1. No chart, due-back player at 18 a game for a player at 10 a game: met by
   `tests/test_rubric.py:1217`. The test asserts Jacobs is the pick.
2. A chart that lists every player gives the same grade: met by code. The trade value branch at `rubric.py:209-210`
   is unchanged. `tests/test_rubric.py:1223` shows the chart decides over a higher projection.
3. Every existing rubric test passes unchanged: the diff removes or edits no test line.
   `uv run pytest -q tests/test_rubric.py` gives `128 passed`.

## Handcuff and no-return trace

- `lineup_value` (`adjusters.py:112`) returns `projection_ahead` only when the projections file exists and
  `_due_back` is true. `_due_back` (`adjusters.py:486`) needs a return week after the last completed week.
- A player with no recent games and no return week: `_due_back` is false, so `recent_points_per_game` gives 0. Same as before.
- A handcuff on the trade value path: `_trade_values` (`rubric.py:155`) sets him to 0. Unchanged.
- A handcuff on the fallback path: he gets his lineup value, not 0. See Minor 1.

## Readers of the pick

`grade` (`rubric.py:230`) passes the pick to `build_side`, which sets `gets_highest_value` and `gives_highest_value`
(`adjusters.py:205-206`). Two adjusters read them:

- Roster fit (`adjusters.py:323`): +1 with the reason "It gets the highest-value player in the trade, and the best
  lineup does not lose." It fires only with no lineup gain and no lineup loss.
- Standing, seller branch (`adjusters.py:394-399`): +1 when the seller gets the pick. -1 when the seller gives
  the pick for a lineup gain now.

Both flips move the step to the side that gets the due-back star. The ticket asks for this. The start letter does
not read the pick. With no chart, both sides start at C, so only these steps move the final letter.

Note, no fix asked: with the change, one due-back player can earn the roster fit +1 and the contender return bet +1 for
the same side. The chart path already allows this pair when a due-back star tops the chart, so the change adds no new kind of grade.

## Real-data check

Data: `data/2026/week-06/raw/`, chart removed, projections file present. Trade: roster 3 gives Stefon Diggs (`2449`),
roster 11 gives Josh Jacobs (`5850`, due back week 7). Lineup values: Diggs 10.17, Jacobs 12.21.
"Before" patches `rubric.lineup_value` back to `recent_points_per_game`, which is the base code.

Before (pick `2449`, Diggs):

```
 roster 3: start C final C
   roster fit +0: The best lineup stays about the same. Josh Jacobs is due back in week 7, so he counts for his projection ahead of 12.2 a game.
   standing +1: The team holds a playoff spot, and Josh Jacobs is due back before the playoffs.
   trend and usage -1: ...
 roster 11: start C final B
   roster fit +1: It gets the highest-value player in the trade, and the best lineup does not lose. Josh Jacobs is due back in week 7, so he counts for his projection ahead of 12.2 a game.
   standing +0: The team is neither in a playoff spot nor out of the race.
   trend and usage +1: ...
```

After (pick `5850`, Jacobs):

```
 roster 3: start C final B
   roster fit +1: It gets the highest-value player in the trade, and the best lineup does not lose. Josh Jacobs is due back in week 7, so he counts for his projection ahead of 12.2 a game.
   standing +1: The team holds a playoff spot, and Josh Jacobs is due back before the playoffs.
   trend and usage -1: ...
 roster 11: start C final B
   roster fit +0: The best lineup stays about the same. Josh Jacobs is due back in week 7, so he counts for his projection ahead of 12.2 a game.
   standing +0: The team is neither in a playoff spot nor out of the race.
   trend and usage +1: ...
```

The builder's claim holds. Roster 3 moves from C to B. Roster 11 stays at B, now from trend alone.

## Missing from the diff

Nothing the ticket asks for. The Status line stays `open`. The orchestrator sets it to done at merge.

## Re-review: fix round 1 (`ba200a5..e974438`)

Verdict: both findings ADDRESSED. The fix diff adds no new breakage.

1. Handcuff at zero: ADDRESSED. `rubric.py:213` sets `Decimal(0)` for each handcuff in the fallback, the same rule
   as `_trade_values`. Test `test_with_no_chart_a_handcuff_due_back_is_never_the_highest_value_player`
   asserts `trade_handcuffs` gives `[MITCHELL]`, so the zero path runs. Without the fix, Mitchell is due back in week 7,
   so `lineup_value` gives his projection of 30 and he beats Pollard. I put the `ba200a5` code back and ran the test.
   The result was `1 failed`.
2. Test through `grade`: ADDRESSED. Test `test_with_no_chart_a_seller_that_gets_a_player_due_back_gets_the_highest_value_player`
   reads the standing step and reason from `grade`. It fails on base `e29e2b4` code and passes on `ba200a5` and `e974438`.

Checks: `uv run pytest -q tests/test_rubric.py` gives `130 passed`. I restored the worktree, and `git status` is clean.
