# Existing README rule execution

Fixed implementation revision: `dad744db4f3b49732adc1586e08c34be2f381f73`.
Execution checkout HEAD: `85d54d463a6bb111bb37c58bd810c24d1d9f4131`.
The orchestrator supplies the commands, working directories, revision, and successful exit status for these exact reruns.
The raw logs below contain the complete output. Each copied file retains its original bytes.
The fixed implementation and execution HEAD differ only in two ticket status records.
The product byte comparison in `../snapshot.json` confirms all 13 documents against the fixed implementation.
The full HEAD delta below also excludes any rule-test or source change.
No rule code changes for this feature. No cold task trial runs.

```text
M	.scratch/readme-module-navigation/issues/01-connect-all-six-navigation-routes.md
M	.scratch/readme-module-navigation/issues/02-prove-all-six-routes-with-cold-agents.md
```

## site

Command: `NODE_OPTIONS=--experimental-strip-types pnpm --dir apps/site exec vitest run src/readme-rule.test.ts`.
Working directory: `/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation`.
Exit status: `0`, reported by the orchestrator.
Observed output: `7` tests pass in the existing rule file.
Raw output: `readme-static-site-rules.log`.
SHA-256: `c0ab87d24ef076d757b1da7f7a0d401bfb439a50334d50a947101aea17483600`.

```text

 RUN  v5.0.5 /Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation/apps/site


 Test Files  1 passed (1)
      Tests  7 passed (7)
   Start at  15:53:42
   Duration  1.05s (environment 93%, tests 4%, transform 1%, import 1%, worker 1%)

```

## pipeline

Command: `uv run --exact --package cornerstone pytest -q tests/test_rule_readmes.py`.
Working directory: `/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation/apps/pipeline`.
Exit status: `0`, reported by the orchestrator.
Observed output: `11` tests pass in the existing rule file.
Raw output: `readme-static-pipeline-rules.log`.
SHA-256: `a6f3daf087c21a9aac6b050a06e523a68e1a4585cd0b994ca01cc2fd4f3c404d`.

```text
Installed 13 packages in 28ms
...........                                                              [100%]
11 passed in 0.05s
```

## api

Command: `uv run --exact --package cpc-api pytest -q tests/test_rule_api.py`.
Working directory: `/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation/apps/api`.
Exit status: `0`, reported by the orchestrator.
Observed output: `5` tests pass in the existing rule file.
Raw output: `readme-static-api-rules.log`.
SHA-256: `d65c4758bf2d509189de8c996eccb9d8303500142a833c2de82e987f1f30d085`.

```text
Uninstalled 4 packages in 3ms
Installed 8 packages in 21ms
.....                                                                    [100%]
5 passed in 0.13s
```

