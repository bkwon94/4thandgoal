# A follow-up in the Thread gets "I can't answer that."

Kind: bug
Status: done
Branch: `bug-chat-follow-ups`.
Source: the session of 2026-11-14.
Boundary: holds. 2 items of one kind; no new term or ADR; no moved seam, because the existing `turns` field carries the context; each done condition is one sentence.

## Items

### 1. A follow-up such as "you sure?" or "thank you" routes to a miss

Done condition: With the turns of a start or sit answer, `route_question` sends "you sure?" and "thank you" to a route other than `miss`, and an off-topic question such as "write me a poem" with the same turns still routes to `miss`.
Method: diagnosing-bugs.
Cause: `decide` in `apps/api/src/cornerstone_api/ask.py` reads only `about_league` and `data_can_answer` before a miss, and a bare "thank you" after an answer scores about 0.4 and 0.04 on them even with the turns, so it always routes to `miss`. The route now asks Jev the Noul `reacts_to_answer` in `ask_wording.py`, and a yes gives a free answer.
Red: at `f4b17769`, `cd apps/api && uv run --exact --package cpc-api pytest -m live -s -q tests/test_ask_follow_ups.py`

```text
'you sure?': free None {'fits_topic': 0.45, 'data_can_answer': 0.58, 'about_league': 0.98, 'abuse': 0.02, 'names_team': 0.02}
'thank you': miss None {'fits_topic': 0.04, 'data_can_answer': 0.04, 'about_league': 0.42, 'abuse': 0.01, 'names_team': 0.01}
'write me a poem': miss None {'fits_topic': 0.02, 'data_can_answer': 0.02, 'about_league': 0.02, 'abuse': 0.01, 'names_team': 0.01}
E       AssertionError: 'thank you' routed to miss
FAILED tests/test_ask_follow_ups.py::test_a_follow_up_after_a_start_or_sit_answer_routes_to_a_miss_only_when_off_topic[thank you-False]
1 failed, 2 passed in 0.75s
```

Green: at `0ebf3af3`, `cd apps/api && uv run --exact --package cpc-api pytest -m live -s -q tests/test_ask_follow_ups.py`

```text
'you sure?': free None {'fits_topic': 0.47, 'data_can_answer': 0.57, 'about_league': 0.98, 'abuse': 0.02, 'reacts_to_answer': 0.99, 'names_team': 0.02}
'thank you': free None {'fits_topic': 0.03, 'data_can_answer': 0.03, 'about_league': 0.42, 'abuse': 0.01, 'reacts_to_answer': 0.99, 'names_team': 0.01}
'write me a poem': miss None {'fits_topic': 0.02, 'data_can_answer': 0.02, 'about_league': 0.02, 'abuse': 0.02, 'reacts_to_answer': 0.02, 'names_team': 0.01}
3 passed in 1.15s
```
Test verdict: PASS

### 2. The free-answer check fails a reply that stands on the earlier answer

Done condition: With the turns of a start or sit answer and no new tool results, the free-answer check passes a reply to "you sure?" that restates a claim of the earlier answer, and still fails a reply with a claim that neither the turns nor the tool results state.
Method: diagnosing-bugs.
Cause: `check_state` in `apps/api/src/cornerstone_api/free_wording.py` puts only `tool_results` in the Jev state, and `CHECK_QUESTION` asks only about them, so a reply to "you sure?" that restates the earlier answer fails at 0.02 twice and gives the honest miss. A follow-up now puts its turns in the check state with `with_turns`, and its Noul asks whether each claim follows from `tool_results` or from an answer in `earlier_turns`.
Red: at `762e7148`, `cd apps/api && uv run --exact --package cpc-api pytest -m live -s -q tests/test_free_answer.py -k real_check`

```text
'Yes. The pick of Konata Mumpfield rests on his matchup, not his projection.': route free, checks ['checking', 'fixing', 'checking', 'failed']
'Yes. Konata Mumpfield scored 31.4 points last week.': route free, checks ['checking', 'fixing', 'checking', 'failed']
E       AssertionError: 'Yes. The pick of Konata Mumpfield rests on his matchup, not his projection.' ended with ['checking', 'fixing', 'checking', 'failed']
1 failed, 1 passed, 62 deselected in 1.89s
```

Green: at `a88ab9de`, `cd apps/api && uv run --exact --package cpc-api pytest -m live -s -q tests/test_free_answer.py -k real_check`

```text
'Yes. The pick of Konata Mumpfield rests on his matchup, not his projection.': route free, checks ['checking', 'checked']
'Yes. Konata Mumpfield scored 31.4 points last week.': route free, checks ['checking', 'fixing', 'checking', 'failed']
2 passed, 62 deselected in 2.12s
```
Test verdict: PASS

## Comments

- Closes with the squash merge of the PR of `bug-chat-follow-ups`. Commits: `f4b17769`, `0ebf3af3`, `762e7148`, `a88ab9de`, `1ed61f19`. Date: 2026-11-14.
- The full API suite gives 578 passed, the live route eval gives 56 of 59 against a bar of 52, and the loop of each item went red, then green.
- A later run can change `CLAUDE_TURNS_LINE` in `chat_turns.py`, which still tells Claude to take no fact from an earlier answer.
- Read 10 files: AGENTS.md, docs/adr/0033-a-quick-run-skips-the-spec-flow.md, .claude/plugin/skills/quick/format.md, .claude/plugin/skills/quick/judge.md, apps/site/src/app/front-door/front-door.tsx, apps/api/src/cornerstone_api/ask.py, apps/api/src/cornerstone_api/ask_wording.py, apps/api/src/cornerstone_api/chat_turns.py, apps/api/src/cornerstone_api/free_wording.py, apps/api/src/cornerstone_api/free_answer.py.
