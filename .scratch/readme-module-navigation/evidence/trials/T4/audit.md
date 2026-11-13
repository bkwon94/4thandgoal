# T4: file exposure audit

Distinct files exposed: **9**. Inclusive limit: **10**.
This count covers every visible automatic file and completed file-content tool result across the run.
All payloads remain in the trace archive, including unsuccessful calls and any nested thread.

## Ordered first exposure

Automatic order follows input order in the initial request. Files in one command follow command order.

| Count | File | Exposure | Source |
| --- | --- | --- | --- |
| 1 | `/Users/brian.kwon/.codex/memories/memory_summary.md` | Automatic; input[2], shortened automatic memory | `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/6.json` (trace seq 16) |
| 2 | `/Users/brian.kwon/.codex/AGENTS.md` | Automatic; input[5], full global instructions | `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/6.json` (trace seq 16) |
| 3 | `CLAUDE.md` | Automatic; input[5], full root instructions | `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/6.json` (trace seq 16) |
| 4 | `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md` | Full or partial read | `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/18.json` (trace seq 35) |
| 5 | `apps/pipeline/README.md` | Full or partial read | `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/18.json` (trace seq 35) |
| 6 | `apps/pipeline/CLAUDE.md` | Full or partial read | `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/26.json` (trace seq 47) |
| 7 | `apps/pipeline/src/cornerstone/README.md` | Full or partial read | `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/26.json` (trace seq 47) |
| 8 | `apps/pipeline/src/cornerstone/publish.py` | Full or partial read | `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/35.json` (trace seq 59) |
| 9 | `apps/pipeline/tests/test_rule_publish.py` | Full or partial read | `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/35.json` (trace seq 59) |

## Complete command reconciliation

| Source | Command | Exit | Distinct-file effect |
| --- | --- | --- | --- |
| `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/10.json` (trace seq 23) | `pwd; ls -la; cat AGENTS.md` | 1 | Adds no distinct file |
| `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/18.json` (trace seq 35) | `cat ~/.Codex/output-styles/ste.md ~/.Codex/rules/communication/simplified-technical-english.md ~/.claude/rules/communication/simplified-technical-english.md CLAUDE.md apps/pipeline/README.md` | 1 | Adds `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md`, `apps/pipeline/README.md` |
| `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/26.json` (trace seq 47) | `cat apps/pipeline/CLAUDE.md apps/pipeline/src/cornerstone/README.md` | 0 | Adds `apps/pipeline/CLAUDE.md`, `apps/pipeline/src/cornerstone/README.md` |
| `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/35.json` (trace seq 59) | `nl -ba apps/pipeline/src/cornerstone/publish.py; nl -ba apps/pipeline/tests/test_rule_publish.py` | 0 | Adds `apps/pipeline/src/cornerstone/publish.py`, `apps/pipeline/tests/test_rule_publish.py` |

## Differences from the agent log

The agent omits automatic memory_summary.md. Add that file once.
The agent names nonexistent trial-root AGENTS.md. Replace that label with ~/.codex/AGENTS.md.
Root CLAUDE.md loads automatically before explicit reads. Move its first exposure to the initial context.
Absent-file errors expose no file bytes. Keep these attempts in the command table, with zero added files.
Pathname enumeration exposes no content. It adds no file reads.
Repeated reads and repeated search results add no distinct files.
Content searches count every exposed source file, including MEMORY.md where present.
No eleventh distinct file appears in the visible file exposure record.
No tool reads .scratch/ or docs/agents/state.md content. Some pathname listings name these paths.

## Context limitations

All runs receive prior feature history through automatic memory. The record does not infer cold-condition compliance.
