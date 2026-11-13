# T1: file exposure audit

Distinct files exposed: **9**. Inclusive limit: **10**.
This count covers every visible automatic file and completed file-content tool result across the run.
All payloads remain in the trace archive, including unsuccessful calls and any nested thread.

## Ordered first exposure

Automatic order follows input order in the initial request. Files in one command follow command order.

| Count | File | Exposure | Source |
| --- | --- | --- | --- |
| 1 | `/Users/brian.kwon/.codex/memories/memory_summary.md` | Automatic; input[2], shortened automatic memory | `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/6.json` (trace seq 16) |
| 2 | `/Users/brian.kwon/.codex/AGENTS.md` | Automatic; input[5], full global instructions | `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/6.json` (trace seq 16) |
| 3 | `CLAUDE.md` | Automatic; input[5], full root instructions | `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/6.json` (trace seq 16) |
| 4 | `apps/site/README.md` | Full or partial read | `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/30.json` (trace seq 51) |
| 5 | `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md` | Full or partial read | `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/42.json` (trace seq 66) |
| 6 | `apps/site/CLAUDE.md` | Full or partial read | `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/46.json` (trace seq 70) |
| 7 | `apps/site/src/lib/data/README.md` | Full or partial read | `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/50.json` (trace seq 74) |
| 8 | `apps/site/src/lib/data/week-data.ts` | Full or partial read | `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/58.json` (trace seq 86) |
| 9 | `apps/site/src/lib/data/week-data.test.ts` | Full or partial read | `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/62.json` (trace seq 90) |

## Complete command reconciliation

| Source | Command | Exit | Distinct-file effect |
| --- | --- | --- | --- |
| `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/10.json` (trace seq 23) | `pwd; ls -a` | 0 | Adds no distinct file |
| `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/19.json` (trace seq 36) | `cat CLAUDE.md` | 0 | Adds no distinct file |
| `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/22.json` (trace seq 39) | `cat ~/.Codex/output-styles/ste.md` | 1 | Adds no distinct file |
| `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/30.json` (trace seq 51) | `cat apps/site/README.md` | 0 | Adds `apps/site/README.md` |
| `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/34.json` (trace seq 55) | `ls -ld ~/.Codex ~/.claude/rules/communication/simplified-technical-english.md ~/.Codex/rules/communication/simplified-technical-english.md` | 1 | Adds no distinct file |
| `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/42.json` (trace seq 66) | `cat ~/.claude/rules/communication/simplified-technical-english.md` | 0 | Adds `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md` |
| `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/46.json` (trace seq 70) | `cat apps/site/CLAUDE.md` | 0 | Adds `apps/site/CLAUDE.md` |
| `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/50.json` (trace seq 74) | `cat apps/site/src/lib/data/README.md` | 0 | Adds `apps/site/src/lib/data/README.md` |
| `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/58.json` (trace seq 86) | `nl -ba apps/site/src/lib/data/week-data.ts` | 0 | Adds `apps/site/src/lib/data/week-data.ts` |
| `trace/trace-1b8e81ec-637b-4cc7-aa55-edd506cdc575-01a1d1a6-886c-7d91-9865-85fa112b3d6b/payloads/62.json` (trace seq 90) | `nl -ba apps/site/src/lib/data/week-data.test.ts` | 0 | Adds `apps/site/src/lib/data/week-data.test.ts` |

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
