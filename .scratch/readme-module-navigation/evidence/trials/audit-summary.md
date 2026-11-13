# Six-trial audit summary

No trial starts in this audit. No Test verdict appears here.

## Counts from visible exposure

| Run | Agent count | Visible audited count | Final response payload |
| --- | ---: | ---: | --- |
| T1 | 8 | 9 | 67.json |
| T2 | 8 | At least 9; encrypted messages prevent a complete total | 124.json |
| T3 | 9 | 10 | 55.json |
| T4 | 8 | 9 | 39.json |
| T5 | 7 | 8 | 39.json |
| T6 | 8 | 9 | 55.json |

Each source path has the form `/tmp/readme-six-trials/T<N>/trace/*/payloads/<number>.json`.
Each run's payload 6 contains initial automatic context.

Each agent log omits automatic `~/.codex/memories/memory_summary.md`.
Each log misnames global `~/.codex/AGENTS.md` as a nonexistent trial-root AGENTS.md.
Correct that path without another count.
Root CLAUDE.md loads automatically. Later reads add no count.
Absent-file attempts expose no content and add no count.
Catalog metadata adds no count under Brian's clarification.

## Automatic prior memory

Each run's payload 6 contains this exact excerpt:

> - Todoist queue and README navigation: todoist-queue, readme-module-navigation, audit.md, cold-agent
>   - desc: Git ticket authority, action queue, audit and README navigation handoff.
>   - learnings: Cold-agent trials were blocked by launcher and Chromium permissions; inspect current evidence. [skysight memory]

T3 payload 23 and T6 payload 27 expose this exact MEMORY.md line:

> 163:- readme-module-navigation uses six routes and a ten-file cold-agent budget; ticket 01 merged into its spec branch, but cold trials and full validation were blocked by launcher/Chromium permissions. Handoff .handoff/readme-module-navigation.md; inspect current evidence. Source: extensions/skysight/resources/2026-11-12T20-50-00-ELxg-10min-memory-summary.md. [skysight memory]

These excerpts contain prior feature status. They contain no expected module or test answers.
The Judge must distinguish persistent memory from conversation inheritance under the approved procedure.
No visible tool call reads `.scratch/` content or `docs/agents/state.md` content.

## T2 encrypted context limit

T2 payload 25 identifies helper `/root/trace_owner` with model `gpt-6.1-sol`.
T2 payload 33 records its first inference request.
Payload 33 input[6] contains the plaintext NEW_TASK header and a separate `encrypted_content` item.
The helper task body is not available as plaintext there.
Payload 46 input[1] contains a plaintext MESSAGE header and a separate `encrypted_content` item.
Payload 24 spawn arguments and payload 37 send arguments also contain encoded message bodies.
Payload 33 exposes global and root instructions; it does not expose a plaintext helper task body.
Payload 123 contains the helper's plaintext final answer.
Other helper send-message bodies also use encoded content.

Nine distinct files appear across visible T2 automatic context and tool results.
Unknown message contents prevent a complete plaintext context audit or an exact all-content exposure claim.
Do not infer what the encrypted bodies contain.

## Other launch facts

All root metadata payloads identify `gpt-6-astra` and `/tmp/readme-navigation-trial-root`.
T2 adds a helper with another model.
T3 payload 37 records a failed helper launch before helper context or extra reads.
Its exact error is:

> collab spawn failed: Fatal error: failed to load model context for thread 01a1d1a8-732b-7b50-b2bc-83c60c445ce9: invalid thread-store request: no rollout found for thread id 01a1d1a8-732b-7b50-b2bc-83c60c445ce9
