# A follow-up in the Thread gets "I can't answer that."

Kind: bug
Status: in-progress
Branch: `bug-chat-follow-ups`.
Source: the session of 2026-11-14.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam, because the existing `turns` field carries the context; the done condition is one sentence.

## Items

### 1. A follow-up such as "you sure?" or "thank you" routes to a miss

Done condition: With the turns of a start or sit answer, `route_question` sends "you sure?" and "thank you" to a route other than `miss`, and an off-topic question such as "write me a poem" with the same turns still routes to `miss`.
Method: diagnosing-bugs.
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Comments
