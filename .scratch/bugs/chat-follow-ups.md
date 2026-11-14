# A follow-up in the Thread gets "I can't answer that."

Kind: bug
Status: in-progress
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
Test verdict: pending

### 2. The free-answer check fails a reply that stands on the earlier answer

Done condition: With the turns of a start or sit answer and no new tool results, the free-answer check passes a reply to "you sure?" that restates a claim of the earlier answer, and still fails a reply with a claim that neither the turns nor the tool results state.
Method: diagnosing-bugs.
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Comments
