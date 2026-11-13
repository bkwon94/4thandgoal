# T4: automatic context inventory

First request: `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/6.json` (trace seq 16). Session metadata: `trace/trace-7e17fb5b-3192-4aa6-b2eb-c9c20bb1d349-01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46/payloads/1.json` (trace seq 2).

The first request contains no earlier conversation messages. It includes automatic memory about prior feature work.
The memory names prior launcher limits and the README navigation handoff. It supplies no expected module or test answer.
This history exposure remains part of the record. No cold-condition compliance claim follows from the fresh process.

| Input index | Content | File accounting |
| --- | --- | --- |
| 0 | Tool schemas | No file read attributed |
| 1 | Harness developer instructions | No source file identified in the request |
| 2 | Memory rules, automatic memory summary, skill catalog | Count memory_summary.md; exclude catalog metadata only |
| 3 | Team role and tool instructions | No source file identified in the request |
| 4 | Delegation constraint | No source file identified in the request |
| 5 | Global AGENTS, root CLAUDE, environment context | Count both source files |
| 6 | Rex terminal context | No source file identified in the request |
| 7 | Exact approved task and procedure | Supplied task, not a file read |

The full global AGENTS and root CLAUDE text match their source files exactly, apart from boundary whitespace.
The synthetic heading names trial-root AGENTS.md. That path does not exist; the global source is ~/.codex/AGENTS.md.
The root CLAUDE file loads before tool calls. Later explicit reads add no count.
The memory summary counts as a partial automatic file exposure.
File paths in instructions and catalogs alone do not expose the named files. Actual skill file reads would count.

The initial skill catalog remains in the request. Brian excludes this metadata only.

Prior feature history excerpt:

```text
- Todoist queue and README navigation: todoist-queue, readme-module-navigation, audit.md, cold-agent
  - desc: Git ticket authority, action queue, audit and README navigation handoff.
  - learnings: Cold-agent trials were blocked by launcher and Chromium permissions; inspect current evidence. [skysight memory]
```
