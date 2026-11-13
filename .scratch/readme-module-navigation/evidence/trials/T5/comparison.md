# T5: chosen paths and reasons

Expected module: `apps/api/src/cornerstone_api/caps.py`.
Expected test: `apps/api/tests/test_caps.py`.
Both chosen paths equal the approved paths. The retained final answer contains both reasons.

Approved reasons:

Module reason: `Caps` counts answers by roster and local calendar day.
Test reason: The test separates yesterday's count from another team's count.

Reason comparison: The module reason names team and calendar-date filters. The test reason separates yesterday from another team today.

Agent answer and ordered log: [agent-final.md](agent-final.md).
Exposure reconciliation: [audit.md](audit.md). Automatic context: [context-inventory.md](context-inventory.md).
Exact prompt: [prompt.txt](prompt.txt). Full terminal output: [stdout.jsonl](stdout.jsonl).
Public trace derivative; [publication scope](../../PUBLICATION.md): [trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/trace.jsonl](trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/trace.jsonl).
