# T3: file exposure audit

Distinct files exposed: **10**. Inclusive limit: **10**.
This count covers every visible automatic file and completed file-content tool result across the run.
All payloads remain in the trace archive, including unsuccessful calls and any nested thread.

## Ordered first exposure

Automatic order follows input order in the initial request. Files in one command follow command order.

| Count | File | Exposure | Source |
| --- | --- | --- | --- |
| 1 | `/Users/brian.kwon/.codex/memories/memory_summary.md` | Automatic; input[2], shortened automatic memory | `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/6.json` (trace seq 16) |
| 2 | `/Users/brian.kwon/.codex/AGENTS.md` | Automatic; input[5], full global instructions | `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/6.json` (trace seq 16) |
| 3 | `CLAUDE.md` | Automatic; input[5], full root instructions | `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/6.json` (trace seq 16) |
| 4 | `apps/pipeline/README.md` | Full or partial read | `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/18.json` (trace seq 35) |
| 5 | `apps/pipeline/CLAUDE.md` | Full or partial read | `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/18.json` (trace seq 35) |
| 6 | `/Users/brian.kwon/.codex/memories/MEMORY.md` | Content search | `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/22.json` (trace seq 39) |
| 7 | `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md` | Full or partial read | `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/30.json` (trace seq 51) |
| 8 | `packages/week/python/src/week/sheet/README.md` | Full or partial read | `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/30.json` (trace seq 51) |
| 9 | `packages/week/python/src/week/sheet/base.py` | Content search | `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/43.json` (trace seq 71) |
| 10 | `apps/pipeline/tests/test_sheet.py` | Content search | `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/43.json` (trace seq 71) |

## Complete command reconciliation

| Source | Command | Exit | Distinct-file effect |
| --- | --- | --- | --- |
| `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/10.json` (trace seq 23) | `pwd; rg --files -g AGENTS.md -g CLAUDE.md -g README.md -g '*playoff*' -g '*roster*' -g '*projection*'` | 0 | Adds no distinct file |
| `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/18.json` (trace seq 35) | `cat /Users/brian.kwon/.Codex/output-styles/ste.md /Users/brian.kwon/.Codex/rules/communication/simplified-technical-english.md CLAUDE.md apps/pipeline/README.md apps/pipeline/CLAUDE.md` | 1 | Adds `apps/pipeline/README.md`, `apps/pipeline/CLAUDE.md` |
| `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/22.json` (trace seq 39) | `rg -n 'readme-module-navigation\|cold-agent' /Users/brian.kwon/.codex/memories/MEMORY.md` | 0 | Adds `/Users/brian.kwon/.codex/memories/MEMORY.md` |
| `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/30.json` (trace seq 51) | `cat /Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md packages/week/python/src/week/sheet/README.md` | 0 | Adds `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md`, `packages/week/python/src/week/sheet/README.md` |
| `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/43.json` (trace seq 71) | `rg -n -C 12 'def projected_totals\|current\|roster\|addition\|drop\|lock' packages/week/python/src/week/sheet/base.py apps/pipeline/tests/test_sheet.py` | 0 | Adds `packages/week/python/src/week/sheet/base.py`, `apps/pipeline/tests/test_sheet.py` |
| `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/50.json` (trace seq 81) | `rg -n -A 55 -B 3 'def test_.*(current\|added\|additions\|lock)\|def projected_totals' packages/week/python/src/week/sheet/base.py apps/pipeline/tests/test_sheet.py` | 0 | Adds no distinct file |

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
A content search also exposes MEMORY.md line 163 about prior feature status and launcher limits.
The helper launch attempt fails before a helper request or extra file read: `trace/trace-0e9396c6-ecce-4125-b193-36a0934c48fa-01a1d1a8-732b-7b50-b2bc-83c60c445ce9/payloads/37.json` (trace seq 62).
