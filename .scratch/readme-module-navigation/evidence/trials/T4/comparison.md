# T4: chosen paths and reasons

Expected module: `apps/pipeline/src/cornerstone/publish.py`.
Expected test: `apps/pipeline/tests/test_rule_publish.py`.
Both chosen paths equal the approved paths. The retained final answer contains both reasons.

Approved reasons:

Module reason: `run_publish` constrains each commit to season paths.
Test reason: Tests cover stray files, other seasons, and files outside season folders.

Reason comparison: The module reason names season-scoped staging and commit paths. The test reason covers stray files and other seasons.

Agent answer and ordered log: [agent-final.md](agent-final.md).
Exposure reconciliation: [audit.md](audit.md). Automatic context: [context-inventory.md](context-inventory.md).
Exact prompt: [prompt.txt](prompt.txt). Full terminal output: [stdout.jsonl](stdout.jsonl).
Public trace derivative; [publication scope](../../PUBLICATION.md): [trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/trace.jsonl](trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/trace.jsonl).
