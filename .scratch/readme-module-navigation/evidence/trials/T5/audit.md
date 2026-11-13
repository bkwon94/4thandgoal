# T5: file exposure audit

Distinct files exposed: **8**. Inclusive limit: **10**.
This count covers every visible automatic file and completed file-content tool result across the run.
All payloads remain in the trace archive, including unsuccessful calls and any nested thread.

## Ordered first exposure

Automatic order follows input order in the initial request. Files in one command follow command order.

| Count | File | Exposure | Source |
| --- | --- | --- | --- |
| 1 | `/Users/brian.kwon/.codex/memories/memory_summary.md` | Automatic; input[2], shortened automatic memory | `trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/payloads/6.json` (trace seq 16) |
| 2 | `/Users/brian.kwon/.codex/AGENTS.md` | Automatic; input[5], full global instructions | `trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/payloads/6.json` (trace seq 16) |
| 3 | `CLAUDE.md` | Automatic; input[5], full root instructions | `trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/payloads/6.json` (trace seq 16) |
| 4 | `apps/api/README.md` | Full or partial read | `trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/payloads/17.json` (trace seq 35) |
| 5 | `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md` | Full or partial read | `trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/payloads/26.json` (trace seq 47) |
| 6 | `apps/api/src/cornerstone_api/README.md` | Full or partial read | `trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/payloads/26.json` (trace seq 47) |
| 7 | `apps/api/src/cornerstone_api/caps.py` | Full or partial read | `trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/payloads/34.json` (trace seq 59) |
| 8 | `apps/api/tests/test_caps.py` | Full or partial read | `trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/payloads/34.json` (trace seq 59) |

## Complete command reconciliation

| Source | Command | Exit | Distinct-file effect |
| --- | --- | --- | --- |
| `trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/payloads/10.json` (trace seq 23) | `pwd; rg --files -g 'AGENTS.md' -g 'README.md' -g 'CLAUDE.md' -g '*allowance*' -g '*quota*' -g '*budget*' -g '*limit*'` | 0 | Adds no distinct file |
| `trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/payloads/17.json` (trace seq 35) | `cat /Users/brian.kwon/.Codex/output-styles/ste.md /Users/brian.kwon/.Codex/rules/communication/simplified-technical-english.md CLAUDE.md apps/api/README.md` | 1 | Adds `apps/api/README.md` |
| `trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/payloads/26.json` (trace seq 47) | `cat /Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md apps/api/src/cornerstone_api/README.md` | 0 | Adds `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md`, `apps/api/src/cornerstone_api/README.md` |
| `trace/trace-9b5f5367-bbae-4c5e-ada6-d2610cb9332a-01a1d1aa-10a7-7293-a822-239beb9975a4/payloads/34.json` (trace seq 59) | `nl -ba apps/api/src/cornerstone_api/caps.py; nl -ba apps/api/tests/test_caps.py` | 0 | Adds `apps/api/src/cornerstone_api/caps.py`, `apps/api/tests/test_caps.py` |

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
