# Ticket 12 spec review: the standing reason names the player due back

Branch `nflverse-12`, commit `f95732f`, base `e29e2b4`.

Verdict: clean. No Critical and no Important findings. Two Minor notes follow.

## Checklist

1. Box 1 is met. `tests/test_rubric.py:1161` asserts the full reason. The code at
   `src/cornerstone/adjusters.py:384` and `:394` makes "The team holds a playoff spot, and the best lineup gains
   after Josh Jacobs returns in week 9." The tail matches the ticket text word for word.
2. Box 2 is met. `test_a_contender_steps_up_for_a_lineup_gain_now` at `tests/test_rubric.py:215` is unchanged and
   still asserts "gains now.".
3. Box 3 is met. The diff adds one test and changes no test. `uv run pytest -q tests/test_rubric.py` gives
   `127 passed`.

## The condition "starts after the trade"

`build_side` sets `starters_after` from `best_lineup` on the roster after the trade (`adjusters.py:203`).
`lineup_change` is the total of that same best lineup minus the total before (`adjusters.py:204`, `:160`).
So a player due back adds to the gain only when he is in `starters_after`. A benched player adds nothing.
The condition is right. The real data shows the bench case:

    London Cooking gets Jonathan Taylor and Josh Jacobs, Jacobs on the bench:
    The team holds a playoff spot, and the best lineup gains now.

Bo Girds gets the same result for Taylor and Jacobs, and for Pickens and Jacobs.

## Builder concern 2

The premise in the review brief is wrong, but the concern is still void. With no projections file,
`lineup_value` gives recent points per game over the last 4 weeks (`adjusters.py:112`). A player who got hurt
inside that window has non-zero recent points, so he can start. The text "after X returns" is still true:
`_due_back` reads the returns file, not the projections file, so he is out now in both cases. No change is needed.

## Real-data result

`make analyze` on week 6 (stats through week 5, Jacobs due back in week 7, projection 12.2 a game):

    uv run cornerstone analyze --season 2026 --week 6 --side 11:5850 --side 3:5947 --asker 3 --no-claude
    Lil Fridge (asked), gives Jakobi Meyers, gets Josh Jacobs:
      Roster fit: one step up. The best lineup gains after the trade. Josh Jacobs is due back in week 7, so he counts for his projection ahead of 12.2 a game.
      Standing: one step up. The team holds a playoff spot, and the best lineup gains after Josh Jacobs returns in week 7.

The builder's live case gave Wicks, who starts, so the lineup stayed about the same. A bench player for Jacobs
gains about 4.96 for Lil Fridge. Brock 'N' Roll (roster 1) and Maye d'force B with U (roster 9) get the same text
for a one-for-one trade of a bench player.

## Minor

1. `src/cornerstone/adjusters.py:380`: a mixed gain reads only "after". Example: Brock 'N' Roll gets Taylor and
   Jacobs, both start, gain 14.3. Taylor alone gains now, but the text says "after Josh Jacobs returns in week 7".
   The ticket allows this. Fix: leave as is, or file a ticket for "gains now, and more after X returns".
2. `tests/test_rubric.py:1161`: no unit test pins the bench case or the two-name join. Fix: add one test where
   the side gets a healthy starter and a benched player due back, and assert "gains now.".

Out of scope, as the builder notes: the seller reason at `adjusters.py:413` still says "for a lineup gain now".
File a follow-up ticket if a seller gain from a player due back matters.
