# T6: file exposure audit

Distinct files exposed: **9**. Inclusive limit: **10**.
This count covers every visible automatic file and completed file-content tool result across the run.
All payloads remain in the trace archive, including unsuccessful calls and any nested thread.

## Ordered first exposure

Automatic order follows input order in the initial request. Files in one command follow command order.

| Count | File | Exposure | Source |
| --- | --- | --- | --- |
| 1 | `/Users/brian.kwon/.codex/memories/memory_summary.md` | Automatic; input[2], shortened automatic memory | `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/6.json` (trace seq 16) |
| 2 | `/Users/brian.kwon/.codex/AGENTS.md` | Automatic; input[5], full global instructions | `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/6.json` (trace seq 16) |
| 3 | `CLAUDE.md` | Automatic; input[5], full root instructions | `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/6.json` (trace seq 16) |
| 4 | `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md` | Full or partial read | `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/26.json` (trace seq 47) |
| 5 | `/Users/brian.kwon/.codex/memories/MEMORY.md` | Content search | `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/26.json` (trace seq 47) |
| 6 | `apps/api/README.md` | Full or partial read | `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/26.json` (trace seq 47) |
| 7 | `packages/analyzer/README.md` | Full or partial read | `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/34.json` (trace seq 59) |
| 8 | `packages/analyzer/python/src/analyzer/ratelimit.py` | Content search | `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/42.json` (trace seq 71) |
| 9 | `apps/api/tests/test_api.py` | Content search | `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/42.json` (trace seq 71) |

## Complete command reconciliation

| Source | Command | Exit | Distinct-file effect |
| --- | --- | --- | --- |
| `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/10.json` (trace seq 23) | `pwd; ls -a` | 0 | Adds no distinct file |
| `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/18.json` (trace seq 35) | `cat /Users/brian.kwon/.Codex/output-styles/ste.md /Users/brian.kwon/.Codex/rules/communication/simplified-technical-english.md CLAUDE.md` | 1 | Adds no distinct file |
| `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/26.json` (trace seq 47) | `cat ~/.claude/rules/communication/simplified-technical-english.md; rg -n 'readme-module-navigation\|readme-navigation' /Users/brian.kwon/.codex/memories/MEMORY.md; cat apps/api/README.md` | 0 | Adds `/Users/brian.kwon/.claude/rules/communication/simplified-technical-english.md`, `/Users/brian.kwon/.codex/memories/MEMORY.md`, `apps/api/README.md` |
| `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/34.json` (trace seq 59) | `cat packages/analyzer/README.md` | 0 | Adds `packages/analyzer/README.md` |
| `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/42.json` (trace seq 71) | `cat packages/analyzer/python/src/analyzer/ratelimit.py; rg -n -C 12 'restart\|429\|grade_limit\|GradeLimiter' apps/api/tests/test_api.py` | 0 | Adds `packages/analyzer/python/src/analyzer/ratelimit.py`, `apps/api/tests/test_api.py` |
| `trace/trace-20dabfa7-109a-4e95-b985-1439a88400ad-01a1d1aa-ad30-7e21-bfb9-5aa328901d56/payloads/50.json` (trace seq 83) | `sed -n '1100,1200p' apps/api/tests/test_api.py` | 0 | Adds no distinct file |

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
