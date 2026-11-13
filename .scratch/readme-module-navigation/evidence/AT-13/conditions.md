# Cold trial conditions

All six root processes use `gpt-6-astra` and implementation revision `dad744db4f3b49732adc1586e08c34be2f381f73`.
The launch command and process cwd both name `/tmp/readme-navigation-trial-root`.
Each root receives its exact approved task and revised common procedure. Prompt bytes match the approved source.
The manifest preserves argv, prompt hashes, timestamps, directory, revision, and exit code.
Every root exits zero; process success alone does not establish trial compliance.

| Task | Root thread | Visible file count | Evidence |
| --- | --- | --- | --- |
| T1 | `01a1d1a6-886c-7d91-9865-85fa112b3d6b` | 9 | [records](../trials/T1/comparison.md) |
| T2 | `01a1d1a7-3ef1-74b0-885e-83b8c015be01` | at least 9 | [records](../trials/T2/comparison.md) |
| T3 | `01a1d1a8-732b-7b50-b2bc-83c60c445ce9` | 10 | [records](../trials/T3/comparison.md) |
| T4 | `01a1d1a9-6bbe-7471-b4a9-bbc89bd3cf46` | 9 | [records](../trials/T4/comparison.md) |
| T5 | `01a1d1aa-10a7-7293-a822-239beb9975a4` | 8 | [records](../trials/T5/comparison.md) |
| T6 | `01a1d1aa-ad30-7e21-bfb9-5aa328901d56` | 9 | [records](../trials/T6/comparison.md) |

[Complete launch manifest](../trials/manifest.json). [Independent context audit](../trials/audit-summary.md).
Each run preserves the full first inference request, all subsequent requests, responses, and tool events.
The first root request contains no earlier conversation messages, but automatic memory exposes prior feature history.
T3 and T6 also read MEMORY.md line 163 about prior trial blockers.
No visible source supplies expected target answers. No visible tool reads the prohibited tracker or state contents.

T2 starts a second agent on `gpt-6.1-sol`. This departs from the approved one-agent and one-model procedure.
Its delegate task and messages remain encrypted. The archive cannot establish their complete plaintext content.
T3 attempts another agent, but that launch fails before any helper context or file read.
These observations remain unresolved against the approved cold-start requirements. No requirement changes here.
