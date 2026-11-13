# Front door trade drops the extra player of a 1-for-2 trade

Kind: bug
Status: in-progress
Branch: `bug-trade-extra-player`.
Source: the queue task `Front door trade drops the extra player of a 1-for-2 trade`.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. Front door trade drops the extra player of a 1-for-2 trade

Done condition: The ask "trade Kyren Williams for Chase Brown and Devonta Smith" gives the trade weigh all three players, with Chase Brown and Devonta Smith both on the side that comes back.
Method: diagnosing-bugs
Cause: `pick_players` in `apps/api/src/cornerstone_api/trade_topics.py` reads one Choice per side, and a Choice picks one player, so the trade check of a 1-for-2 trade keeps only the first player that the manager gets.
Red: at `a79f8498`, `cd apps/api && uv run --exact --package cpc-api pytest -q tests/test_trade_topics.py -k one_for_two`

```text
>       assert [player["name"] for player in yours["gets"]] == ["Chase Brown", "DeVonta Smith"]
E       AssertionError: assert ['Chase Brown'] == ['Chase Brown...eVonta Smith']
E         Right contains one more item: 'DeVonta Smith'
FAILED tests/test_trade_topics.py::test_a_typed_one_for_two_trade_weighs_all_three_players
1 failed, 40 deselected in 2.04s
```

Green: at `a62168c0`, `cd apps/api && uv run --exact --package cpc-api pytest -q tests/test_trade_topics.py -k one_for_two`

```text
.                                                                        [100%]
1 passed, 40 deselected in 2.50s
```

Test verdict: PASS

## Comments
