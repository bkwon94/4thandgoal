# A trade check drops a player of a side of three or more

Kind: bug
Status: in-progress
Branch: `bug-three-player-side`.
Source: the queue task `Front door trade drops a player of a 3-or-more trade side`.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. Front door trade drops a player of a 3-or-more trade side

Done condition: A typed trade check that names three or more players on one side, such as "trade Kyren Williams for Chase Brown, Ja'Marr Chase, and Devonta Smith", never weighs a trade without one of the named players, and the ask opens the trade form with each sure player instead, while a 2-for-2 and a 3-for-1 check also have tests.
Method: diagnosing-bugs
Cause: `pick_players` in `apps/api/src/cornerstone_api/trade_topics.py` reads one Choice for the first player and one for the last player of each side, and no Noul of `pick_questions` asks about a third player, so `Pick.sure` holds for a side of three and the trade check weighs a trade without its middle player.
Red: at `524e23b2`, `cd apps/api && uv run --exact --package cpc-api pytest -q tests/test_trade_topics.py -k "two_for_two or three_players or three_for_one or one_for_two"`

```text
E       AssertionError: weighed a trade of only [['Kyren Williams'], ['Chase Brown', 'DeVonta Smith']]
E       AssertionError: weighed a trade of only [['Kyren Williams', 'Trey McBride'], ['Saquon Barkley']]
FAILED tests/test_trade_topics.py::test_a_typed_trade_that_gets_three_players_opens_the_form_with_each_sure_player
FAILED tests/test_trade_topics.py::test_a_typed_three_for_one_trade_opens_the_form_with_each_sure_player
2 failed, 2 passed, 40 deselected in 6.77s
```

Green: at `29ce51bb`, `cd apps/api && uv run --exact --package cpc-api pytest -q tests/test_trade_topics.py -k "two_for_two or three_players or three_for_one or one_for_two"`

```text
....                                                                     [100%]
4 passed, 40 deselected in 4.53s
```
Test verdict: PASS

## Comments
