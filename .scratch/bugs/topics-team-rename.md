# The power rankings test expects an old team name

Kind: bug
Status: done
Branch: `bug-topics-team-rename`.
Source: the session of 2026-11-17.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The power rankings test expects an old team name

Done condition: `tests/test_topics.py::test_the_power_rankings_block_lists_each_team_with_its_rank_and_its_move` passes on the published cpc data after the week 10 publish.
Method: diagnosing-bugs
Cause: `test_the_power_rankings_block_lists_each_team_with_its_rank_and_its_move` in `apps/pipeline/tests/test_topics.py` expects "London Cooking" at rank 5, but the week 10 publish rewrote the week 9 rows of `clients/cpc/published/2026/rankings.json` with the current name "Puka Deez...". Ranks and moves did not change.
Red: at `62b1e3ca`, `cd apps/pipeline && uv run --exact --package cornerstone pytest tests/test_topics.py -k power_rankings -q`

```text
E         At index 4 diff: (5, 'Puka Deez...', 3) != (5, 'London Cooking', 3)
FAILED tests/test_topics.py::test_the_power_rankings_block_lists_each_team_with_its_rank_and_its_move
1 failed, 12 deselected in 0.64s
```

Green: at `123926d4`, `cd apps/pipeline && uv run --exact --package cornerstone pytest tests/test_topics.py -k power_rankings -q`

```text
.                                                                        [100%]
1 passed, 12 deselected in 0.64s
```
Test verdict: PASS

## Comments
- Closes with the squash merge of the PR of `bug-topics-team-rename`. Commits: `62b1e3ca`, `123926d4`, `c42d8ad2`. Date: 2026-11-17.
- The loop went red at `62b1e3ca` and green at `123926d4`, and all 13 tests of `tests/test_topics.py` pass.
- `test_the_cpc_ladder_block_lists_each_team_by_standing_with_its_odds_and_the_playoff_line` also expects the old name and can fail on a later rewrite; a fixed copy of the data fixes both tests.
- Read 4 files: apps/pipeline/tests/test_topics.py, clients/cpc/published/2026/rankings.json, .claude/plugin/skills/quick/format.md, AGENTS.md.
