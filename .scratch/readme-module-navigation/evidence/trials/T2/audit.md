# T2: file exposure audit

Visible distinct files exposed: **at least 9**. Inclusive limit: **10**.
This count covers every visible automatic file and completed file-content tool result across the run.
All payloads remain in the trace archive, including unsuccessful calls and any nested thread.

## Ordered first exposure

Automatic order follows input order in the initial request. Files in one command follow command order.

| Count | File | Exposure | Source |
| --- | --- | --- | --- |
| 1 | `/Users/brian.kwon/.codex/memories/memory_summary.md` | Automatic; input[2], shortened automatic memory | `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/6.json` (trace seq 16) |
| 2 | `/Users/brian.kwon/.codex/AGENTS.md` | Automatic; input[5], full global instructions | `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/6.json` (trace seq 16) |
| 3 | `CLAUDE.md` | Automatic; input[5], full root instructions | `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/6.json` (trace seq 16) |
| 4 | `apps/site/README.md` | Full or partial read | `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/42.json` (trace seq 76) |
| 5 | `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md` | Full or partial read | `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/53.json` (trace seq 92) |
| 6 | `apps/site/CLAUDE.md` | Full or partial read | `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/61.json` (trace seq 103) |
| 7 | `packages/analyzer/site/form/README.md` | Full or partial read | `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/69.json` (trace seq 114) |
| 8 | `packages/analyzer/site/form/team-picker.tsx` | Full or partial read | `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/91.json` (trace seq 146) |
| 9 | `packages/analyzer/site/form/team-picker.test.tsx` | Full or partial read | `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/102.json` (trace seq 163) |

## Complete command reconciliation

| Source | Command | Exit | Distinct-file effect |
| --- | --- | --- | --- |
| `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/10.json` (trace seq 23) | `pwd; ls -a` | 0 | Adds no distinct file |
| `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/18.json` (trace seq 35) | `cat CLAUDE.md ~/.Codex/output-styles/ste.md ~/.Codex/rules/communication/simplified-technical-english.md` | 1 | Adds no distinct file |
| `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/42.json` (trace seq 76) | `ls -l ~/.claude/rules/communication/simplified-technical-english.md; cat apps/site/README.md` | 0 | Adds `apps/site/README.md` |
| `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/53.json` (trace seq 92) | `cat /Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md` | 0 | Adds `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md` |
| `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/61.json` (trace seq 103) | `cat apps/site/CLAUDE.md` | 0 | Adds `apps/site/CLAUDE.md` |
| `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/69.json` (trace seq 114) | `nl -ba packages/analyzer/site/form/README.md` | 0 | Adds `packages/analyzer/site/form/README.md` |
| `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/91.json` (trace seq 146) | `nl -ba packages/analyzer/site/form/team-picker.tsx` | 0 | Adds `packages/analyzer/site/form/team-picker.tsx` |
| `trace/trace-7da30ae1-f6d9-496a-a372-2cb8b46fd435-01a1d1a7-3ef1-74b0-885e-83b8c015be01/payloads/102.json` (trace seq 163) | `nl -ba packages/analyzer/site/form/team-picker.test.tsx` | 0 | Adds `packages/analyzer/site/form/team-picker.test.tsx` |

## Differences from the agent log

The agent omits automatic memory_summary.md. Add that file once.
The agent names nonexistent trial-root AGENTS.md. Replace that label with ~/.codex/AGENTS.md.
Root CLAUDE.md loads automatically before explicit reads. Move its first exposure to the initial context.
Absent-file errors expose no file bytes. Keep these attempts in the command table, with zero added files.
Pathname enumeration exposes no content. It adds no file reads.
Repeated reads and repeated search results add no distinct files.
Content searches count every exposed source file, including MEMORY.md where present.
No eleventh distinct file appears in visible results. Encrypted messages prevent proof of the complete total.
No tool reads .scratch/ or docs/agents/state.md content. Some pathname listings name these paths.

## Context limitations

All runs receive prior feature history through automatic memory. The record does not infer cold-condition compliance.
T2 starts a helper on gpt-6.1-sol. The approved one-agent and one-model conditions are not established.
The helper uses the same nine distinct files as the visible union. It adds no tenth file.
Delegate message bodies remain encrypted in the full local originals. Public values have explicit redaction markers.
Their plaintext and any hidden file exposure cannot be independently reconciled.
Nine is a lower bound on file exposure. Full plaintext context completeness remains unproven.
