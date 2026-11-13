# Pick owner: week_moves names the first owner of a traded pick

Kind: bug
Status: in-progress
Branch: `bug-pick-owner`.
Source: the queue task `Pick owner: week_moves names the first owner of a traded pick`.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. week_moves names the first owner of a traded pick

Done condition: `week_moves` in `apps/api/src/cornerstone_api/free_tools.py` names the manager who receives a traded pick from `owner_id`, not the first owner in `roster_id`.
Method: diagnosing-bugs
Cause: `week_moves` in `apps/api/src/cornerstone_api/free_tools.py` reads `pick.roster_id`, the first owner of a traded pick, so it names that roster and not `owner_id`, the roster that receives the pick.
Red: at `87342a8a`, `cd apps/api && uv run --exact --package cpc-api pytest -q tests/test_week_moves.py`

```text
>       assert moved["draft_picks"] == ["2027 round 2 to roster 6"]
E       AssertionError: assert ['2027 round 2 to roster 2'] == ['2027 round 2 to roster 6']
E         At index 0 diff: '2027 round 2 to roster 2' != '2027 round 2 to roster 6'
FAILED tests/test_week_moves.py::test_a_traded_pick_goes_to_the_roster_that_receives_it
1 failed in 0.71s
```

Green: at `ef0265bb`, `cd apps/api && uv run --exact --package cpc-api pytest -q tests/test_week_moves.py`

```text
.                                                                        [100%]
1 passed in 0.64s
```
Test verdict: pending

## Comments
